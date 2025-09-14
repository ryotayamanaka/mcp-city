#!/usr/bin/env python3
"""
自动更新 requirements.txt 文件的脚本
使用 uv pip freeze 获取当前环境的包版本并更新 requirements.txt
"""

import subprocess
import sys
from pathlib import Path

def get_installed_packages():
    """使用 uv pip freeze 获取已安装的包列表"""
    try:
        result = subprocess.run(
            ['uv', 'pip', 'freeze'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"错误：无法获取已安装的包列表: {e}")
        sys.exit(1)

def parse_requirements(requirements_file):
    """解析现有的 requirements.txt 文件"""
    if not requirements_file.exists():
        return {}
    
    packages = {}
    with open(requirements_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # 处理包名和版本
                if '==' in line:
                    name, version = line.split('==', 1)
                    packages[name.lower().strip()] = line
                elif '>=' in line or '<=' in line or '~=' in line:
                    name = line.split('[')[0].split('>')[0].split('<')[0].split('~')[0]
                    packages[name.lower().strip()] = line
                else:
                    packages[line.lower().strip()] = line
    
    return packages

def update_requirements(requirements_file, packages_to_track):
    """更新 requirements.txt 文件，只更新指定的包"""
    installed_packages = get_installed_packages()
    
    # 创建已安装包的字典
    installed_dict = {}
    for package in installed_packages:
        if '==' in package:
            name, version = package.split('==', 1)
            installed_dict[name.lower()] = package
    
    # 读取现有的 requirements.txt
    existing_packages = parse_requirements(requirements_file)
    
    # 更新指定的包
    updated_packages = existing_packages.copy()
    
    for package_name in packages_to_track:
        package_lower = package_name.lower()
        # 检查是否有带 extras 的包（如 anthropic[bedrock]）
        base_package = package_lower.split('[')[0]
        
        if base_package in installed_dict:
            # 保留 extras 信息
            if '[' in package_name:
                extras = package_name[package_name.index('['):]
                base_name, version = installed_dict[base_package].split('==')
                updated_packages[package_lower] = f"{package_name.split('[')[0]}{extras}=={version}"
            else:
                updated_packages[package_lower] = installed_dict[base_package]
        elif package_lower in installed_dict:
            updated_packages[package_lower] = installed_dict[package_lower]
    
    # 写入更新后的 requirements.txt
    with open(requirements_file, 'w') as f:
        for package in sorted(updated_packages.values(), key=lambda x: x.lower()):
            f.write(f"{package}\n")
    
    print(f"✅ 已更新 {requirements_file}")
    print("\n更新后的包列表：")
    for package in sorted(updated_packages.values(), key=lambda x: x.lower()):
        print(f"  {package}")

def main():
    """主函数"""
    # 设置要跟踪的包
    packages_to_track = [
        'fastapi',
        'uvicorn[standard]',
        'pydantic',
        'requests',
        'agno',
        'google-genai',
        'sqlalchemy',
        'anthropic[bedrock]'  # 新添加的包
    ]
    
    # requirements.txt 文件路径
    requirements_file = Path(__file__).parent / 'requirements.txt'
    
    print("🔄 正在更新 requirements.txt...")
    update_requirements(requirements_file, packages_to_track)

if __name__ == '__main__':
    main()
