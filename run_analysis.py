#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本
按顺序运行政府基金分析和GDP回归分析
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"正在执行: {description}")
    print(f"命令: {command}")
    print(f"{'='*60}")
    
    try:
        # 运行命令
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        # 显示输出
        if result.stdout:
            print("标准输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        # 检查返回码
        if result.returncode == 0:
            print(f"✓ {description} 执行成功")
            return True
        else:
            print(f"✗ {description} 执行失败 (返回码: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"✗ 执行 {description} 时发生异常: {e}")
        return False

def check_files():
    """检查必要的文件是否存在"""
    print("检查必要文件...")
    
    required_files = ['govfund_filtered.xlsx', 'gdp.xlsx']
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024
            print(f"✓ {file} 存在 ({size:.1f} KB)")
        else:
            print(f"✗ {file} 不存在")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n缺少必要文件: {missing_files}")
        print("请确保以下文件存在于当前目录:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    return True

def main():
    """主函数"""
    print("政府基金分析与GDP回归分析 - 快速启动")
    print("=" * 60)
    
    # 显示当前工作目录
    print(f"当前工作目录: {os.getcwd()}")
    
    # 检查文件
    if not check_files():
        print("\n文件检查失败，程序终止")
        return
    
    print("\n开始执行分析流程...")
    
    # 步骤1: 运行基金分析
    success1 = run_command(
        "python analyze_govfund.py",
        "政府基金数据分析"
    )
    
    if not success1:
        print("\n基金分析失败，程序终止")
        return
    
    # 等待一下，确保文件写入完成
    print("等待文件写入完成...")
    time.sleep(2)
    
    # 检查分析结果文件是否生成
    if not os.path.exists('govfund_analysis_results.xlsx'):
        print("✗ 未找到分析结果文件，请检查基金分析是否成功")
        return
    
    print("✓ 基金分析结果文件已生成")
    
    # 步骤2: 运行GDP回归分析
    success2 = run_command(
        "python gdp_regression.py",
        "GDP回归分析"
    )
    
    if not success2:
        print("\nGDP回归分析失败")
        return
    
    print("\n" + "="*60)
    print("🎉 所有分析完成！")
    print("="*60)
    
    # 显示生成的文件
    print("\n生成的结果文件:")
    result_files = [
        'govfund_analysis_results.xlsx',
        'gdp_fund_regression_results.xlsx'
    ]
    
    for file in result_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024
            print(f"  ✓ {file} ({size:.1f} KB)")
        else:
            print(f"  ✗ {file} (未生成)")
    
    print("\n分析流程完成！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断程序")
    except Exception as e:
        print(f"\n程序执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
