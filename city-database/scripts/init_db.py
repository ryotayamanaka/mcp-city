#!/usr/bin/env python3
"""
安全なデータベース初期化スクリプト
- 冪等性を保証
- 初期化状態を追跡
- エラーハンドリング
"""

import os
import sys
import duckdb
import hashlib
from pathlib import Path

# 設定
DB_PATH = os.getenv("DUCKDB_DATABASE", "/database/city.db")
SCRIPTS_DIR = "/scripts"
DATA_DIR = "/data"
INIT_FLAG_FILE = "/database/.initialized"

def get_data_hash():
    """CSVファイルのハッシュ値を計算してデータ変更を検出"""
    hash_obj = hashlib.md5()
    
    csv_files = ["residents.csv", "tenant.csv", "traffic.csv"]
    for csv_file in csv_files:
        file_path = Path(DATA_DIR) / csv_file
        if file_path.exists():
            with open(file_path, 'rb') as f:
                hash_obj.update(f.read())
        else:
            print(f"Warning: {csv_file} not found")
    
    return hash_obj.hexdigest()

def is_already_initialized():
    """初期化済みかチェック"""
    if not os.path.exists(INIT_FLAG_FILE):
        return False
    
    try:
        with open(INIT_FLAG_FILE, 'r') as f:
            stored_hash = f.read().strip()
        
        current_hash = get_data_hash()
        return stored_hash == current_hash
    except:
        return False

def mark_initialized():
    """初期化完了をマーク"""
    current_hash = get_data_hash()
    with open(INIT_FLAG_FILE, 'w') as f:
        f.write(current_hash)

def verify_database():
    """データベースの整合性を確認"""
    try:
        conn = duckdb.connect(DB_PATH)
        
        # テーブル存在確認
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [table[0] for table in tables]
        
        expected_tables = ["residents", "tenant", "traffic"]
        missing_tables = [t for t in expected_tables if t not in table_names]
        
        if missing_tables:
            print(f"Missing tables: {missing_tables}")
            return False
        
        # データ存在確認
        for table in expected_tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"Table {table}: {count} rows")
            if count == 0:
                print(f"Warning: {table} is empty")
                return False
        
        conn.close()
        return True
    except Exception as e:
        print(f"Database verification failed: {e}")
        return False

def initialize_database():
    """データベースを初期化"""
    print("Initializing database...")
    
    try:
        # 安全な初期化スクリプトを使用
        script_path = Path(SCRIPTS_DIR) / "init_database_safe.sql"
        
        if not script_path.exists():
            print(f"Error: {script_path} not found")
            return False
        
        conn = duckdb.connect(DB_PATH)
        
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # スクリプトを実行
        conn.execute(sql_content)
        conn.close()
        
        # 検証
        if verify_database():
            mark_initialized()
            print("Database initialization completed successfully!")
            return True
        else:
            print("Database verification failed after initialization")
            return False
            
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False

def main():
    """メイン処理"""
    print("=== City Database Initialization ===")
    
    # データベースディレクトリ作成
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # 初期化チェック
    if is_already_initialized():
        print("Database already initialized and up-to-date.")
        if verify_database():
            print("Database verification passed.")
            return True
        else:
            print("Database verification failed. Re-initializing...")
    
    # 初期化実行
    return initialize_database()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
