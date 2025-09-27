from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional, List, Dict, Any
import duckdb
import os
import requests

app = FastAPI(title="City Database API", description="HTTP API for city DuckDB with API-key auth via city-devices")

DUCKDB_DATABASE = os.getenv("DUCKDB_DATABASE", "/database/city.db")
AUTH_VALIDATE_URL = os.getenv("AUTH_VALIDATE_URL", "http://city-devices-api:8000/auth/me")

# Whitelist: allowed tables and columns (expand as needed)
ALLOWED_TABLES: Dict[str, List[str]] = {
    "residents": ["id", "name", "age", "district", "occupation", "income", "family_size"],
    "tenant": ["id", "name", "type", "district", "revenue", "employees", "established_year"],
    "traffic": ["datetime", "location", "vehicle_count", "avg_speed", "traffic_level", "weather"],
}
MAX_LIMIT = 1000
MAX_OFFSET = 5000


def validate_api_key(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="認証が必要です")
    try:
        resp = requests.get(AUTH_VALIDATE_URL, headers={"Authorization": authorization}, timeout=5)
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="無効な認証情報です")
        return resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"認証サービスに接続できません: {e}")


def connect_db():
    try:
        return duckdb.connect(DUCKDB_DATABASE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB接続に失敗しました: {e}")


@app.get("/db/health")
def health():
    return {"status": "ok", "database": DUCKDB_DATABASE}


@app.get("/db/tables")
def list_tables(_user: Dict[str, Any] = Depends(validate_api_key)):
    conn = connect_db()
    try:
        result = {}
        for table_name, allowed_cols in ALLOWED_TABLES.items():
            # Use whitelist rather than SHOW/DESCRIBE
            count = conn.sql(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            result[table_name] = {
                "columns": [{"name": c, "type": "unknown"} for c in allowed_cols],
                "row_count": count,
            }
        return {"success": True, "tables": result}
    finally:
        conn.close()


@app.post("/db/query")
def run_query(payload: Dict[str, Any], _user: Dict[str, Any] = Depends(validate_api_key)):
    # Keep for admin use; default reject
    raise HTTPException(status_code=403, detail="このエンドポイントは管理者専用です")


@app.get("/db/sample")
def sample(table: str, limit: int = 10, _user: Dict[str, Any] = Depends(validate_api_key)):
    if table not in ALLOWED_TABLES:
        raise HTTPException(status_code=400, detail="許可されていないテーブルです")
    lim = max(1, min(limit, MAX_LIMIT))
    cols = ",".join(ALLOWED_TABLES[table])
    conn = connect_db()
    try:
        cur = conn.execute(f"SELECT {cols} FROM {table} LIMIT ?", [lim])
        rows = cur.fetchall()
        colnames = [d[0] for d in cur.description]
        data = [dict(zip(colnames, r)) for r in rows]
        return {"success": True, "row_count": len(data), "columns": colnames, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQLエラー: {e}")
    finally:
        conn.close()


@app.post("/db/select")
def select_rows(payload: Dict[str, Any], _user: Dict[str, Any] = Depends(validate_api_key)):
    table = payload.get("table")
    if table not in ALLOWED_TABLES:
        raise HTTPException(status_code=400, detail="許可されていないテーブルです")

    req_cols = payload.get("columns")
    columns = ALLOWED_TABLES[table] if not req_cols else [c for c in req_cols if c in ALLOWED_TABLES[table]]
    if not columns:
        raise HTTPException(status_code=400, detail="列が不正です")

    filters = payload.get("filters", {})  # {col: {op: "=|IN|BETWEEN", value: ...}}
    order_by = payload.get("order_by", [])  # [{column, dir}]
    limit = payload.get("limit", 100)
    offset = payload.get("offset", 0)

    # Guard limits
    try:
        limit = int(limit)
        offset = int(offset)
    except Exception:
        raise HTTPException(status_code=400, detail="limit/offset は整数で指定してください")
    if limit < 1 or limit > MAX_LIMIT:
        limit = min(max(limit, 1), MAX_LIMIT)
    if offset < 0 or offset > MAX_OFFSET:
        offset = min(max(offset, 0), MAX_OFFSET)

    # Build WHERE clause safely
    where_clauses = []
    params: List[Any] = []
    allowed_ops = {"=", "IN", "BETWEEN"}
    for col, cond in filters.items():
        if col not in ALLOWED_TABLES[table]:
            continue
        op = str(cond.get("op", "=")).upper()
        val = cond.get("value")
        if op not in allowed_ops:
            continue
        if op == "=":
            where_clauses.append(f"{col} = ?")
            params.append(val)
        elif op == "IN":
            if not isinstance(val, list) or not val:
                continue
            placeholders = ",".join(["?"] * len(val))
            where_clauses.append(f"{col} IN ({placeholders})")
            params.extend(val)
        elif op == "BETWEEN":
            if not isinstance(val, list) or len(val) != 2:
                continue
            where_clauses.append(f"{col} BETWEEN ? AND ?")
            params.extend(val)

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # ORDER BY
    order_sql_parts: List[str] = []
    for spec in order_by:
        c = spec.get("column")
        d = str(spec.get("dir", "asc")).lower()
        if c in ALLOWED_TABLES[table] and d in {"asc", "desc"}:
            order_sql_parts.append(f"{c} {d}")
    order_sql = (" ORDER BY " + ", ".join(order_sql_parts)) if order_sql_parts else ""

    cols_sql = ",".join(columns)
    sql = f"SELECT {cols_sql} FROM {table}{where_sql}{order_sql} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    conn = connect_db()
    try:
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        colnames = [d[0] for d in cur.description]
        data = [dict(zip(colnames, r)) for r in rows]
        return {"success": True, "row_count": len(data), "columns": colnames, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQLエラー: {e}")
    finally:
        conn.close()


