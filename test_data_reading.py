#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据读取测试脚本
用于验证GDP和基金数据的读取功能
"""

import pandas as pd
import os
import traceback

def test_gdp_file():
    """测试GDP文件读取"""
    print("=== 测试GDP文件读取 ===")
    
    file_path = 'gdp.xlsx'
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 - {file_path}")
        return False
    
    try:
        # 尝试读取文件
        df = pd.read_excel(file_path)
        print(f"✓ 成功读取GDP文件")
        print(f"  文件大小: {os.path.getsize(file_path) / 1024:.1f} KB")
        print(f"  数据形状: {df.shape}")
        print(f"  列名: {list(df.columns)}")
        
        # 检查列名
        print("\n列名详情:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. {col}")
        
        # 检查数据类型
        print("\n数据类型:")
        print(df.dtypes)
        
        # 检查前几行数据
        print("\n前5行数据:")
        print(df.head())
        
        # 检查是否有空值
        print("\n空值统计:")
        null_counts = df.isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                print(f"  {col}: {count} 个空值")
        
        return True
        
    except Exception as e:
        print(f"✗ 读取GDP文件失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        traceback.print_exc()
        return False

def test_govfund_file():
    """测试政府基金文件读取"""
    print("\n=== 测试政府基金文件读取 ===")
    
    file_path = 'govfund_filtered.xlsx'
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 - {file_path}")
        return False
    
    try:
        # 尝试读取文件
        df = pd.read_excel(file_path)
        print(f"✓ 成功读取政府基金文件")
        print(f"  文件大小: {os.path.getsize(file_path) / 1024:.1f} KB")
        print(f"  数据形状: {df.shape}")
        print(f"  列名: {list(df.columns)}")
        
        # 检查列名
        print("\n列名详情:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. {col}")
        
        # 检查数据类型
        print("\n数据类型:")
        print(df.dtypes)
        
        # 检查前几行数据
        print("\n前5行数据:")
        print(df.head())
        
        # 检查是否有空值
        print("\n空值统计:")
        null_counts = df.isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                print(f"  {col}: {count} 个空值")
        
        return True
        
    except Exception as e:
        print(f"✗ 读取政府基金文件失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        traceback.print_exc()
        return False

def test_analysis_results():
    """测试分析结果文件读取"""
    print("\n=== 测试分析结果文件读取 ===")
    
    file_path = 'govfund_analysis_results.xlsx'
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"警告: 分析结果文件不存在 - {file_path}")
        print("  请先运行 analyze_govfund.py 生成分析结果")
        return False
    
    try:
        # 尝试读取文件
        xl_file = pd.ExcelFile(file_path)
        print(f"✓ 成功读取分析结果文件")
        print(f"  文件大小: {os.path.getsize(file_path) / 1024:.1f} KB")
        print(f"  Sheet数量: {len(xl_file.sheet_names)}")
        print(f"  Sheet名称: {xl_file.sheet_names}")
        
        # 检查每个sheet
        for sheet_name in xl_file.sheet_names:
            print(f"\n--- Sheet: {sheet_name} ---")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"  数据形状: {df.shape}")
            print(f"  列名: {list(df.columns)}")
            print(f"  前3行数据:")
            print(df.head(3))
        
        return True
        
    except Exception as e:
        print(f"✗ 读取分析结果文件失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("数据读取功能测试")
    print("=" * 50)
    
    # 显示当前工作目录
    print(f"当前工作目录: {os.getcwd()}")
    print(f"当前目录文件列表:")
    for file in os.listdir('.'):
        if file.endswith('.xlsx') or file.endswith('.py'):
            file_size = os.path.getsize(file) / 1024
            print(f"  {file} ({file_size:.1f} KB)")
    
    print("\n" + "=" * 50)
    
    # 测试各个文件
    gdp_ok = test_gdp_file()
    govfund_ok = test_govfund_file()
    results_ok = test_analysis_results()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"  GDP文件: {'✓ 正常' if gdp_ok else '✗ 异常'}")
    print(f"  政府基金文件: {'✓ 正常' if govfund_ok else '✗ 异常'}")
    print(f"  分析结果文件: {'✓ 正常' if results_ok else '✗ 异常'}")
    
    if gdp_ok and govfund_ok:
        print("\n✓ 基础数据文件正常，可以运行分析脚本")
        if results_ok:
            print("✓ 分析结果文件存在，可以运行回归分析")
        else:
            print("⚠ 需要先运行 analyze_govfund.py 生成分析结果")
    else:
        print("\n✗ 基础数据文件异常，请检查文件路径和格式")

if __name__ == "__main__":
    main()
