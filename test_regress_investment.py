#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试包含投资数据的regress.py功能
"""

import pandas as pd
import os
import traceback

def test_investment_file():
    """测试固定资产投资文件"""
    print("=== 测试固定资产投资文件 ===")
    
    file_path = '2003-2023各省分行业全社会固定资产投资额.xlsx'
    
    if not os.path.exists(file_path):
        print(f"✗ 文件不存在: {file_path}")
        return False
    
    try:
        # 读取Excel文件
        xl_file = pd.ExcelFile(file_path)
        print(f"✓ 文件存在")
        print(f"  Sheet数量: {len(xl_file.sheet_names)}")
        print(f"  Sheet名称: {xl_file.sheet_names}")
        
        # 检查第一个sheet
        sheet_name = xl_file.sheet_names[0]
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"  使用Sheet: {sheet_name}")
        print(f"  数据形状: {df.shape}")
        print(f"  列名: {list(df.columns)}")
        
        # 查找总投资列
        total_cols = [col for col in df.columns if any(keyword in col for keyword in ['总', '合计', '总计', '全社会'])]
        if total_cols:
            print(f"  找到总投资列: {total_cols}")
        else:
            print(f"  未找到明确的总投资列")
        
        # 检查前几行数据
        print(f"  前5行数据:")
        print(df.head())
        
        return True
        
    except Exception as e:
        print(f"✗ 读取文件失败: {e}")
        traceback.print_exc()
        return False

def test_data_integration():
    """测试数据整合"""
    print("\n=== 测试数据整合 ===")
    
    try:
        # 检查所有必要文件
        required_files = [
            'gdp.xlsx', 
            'govfund_analysis_results.xlsx', 
            '2003-2023各省分行业全社会固定资产投资额.xlsx',
            '2000-2023年各省份城镇化水平.xlsx'
        ]
        
        missing_files = []
        for file in required_files:
            if os.path.exists(file):
                size = os.path.getsize(file) / 1024
                print(f"✓ {file} 存在 ({size:.1f} KB)")
            else:
                print(f"✗ {file} 不存在")
                missing_files.append(file)
        
        if missing_files:
            print(f"\n缺少文件: {missing_files}")
            return False
        
        # 测试数据读取
        print("\n测试数据读取...")
        
        # GDP数据
        gdp_df = pd.read_excel('gdp.xlsx')
        print(f"  GDP数据: {gdp_df.shape}")
        
        # 基金数据
        fund_df = pd.read_excel('govfund_analysis_results.xlsx', sheet_name='年份省份统计')
        print(f"  基金数据: {fund_df.shape}")
        
        # 投资数据
        investment_df = pd.read_excel('2003-2023各省分行业全社会固定资产投资额.xlsx')
        print(f"  投资数据: {investment_df.shape}")
        
        # 城镇化数据
        urban_df = pd.read_excel('2000-2023年各省份城镇化水平.xlsx', sheet_name='原始版本', index_col=0)
        print(f"  城镇化数据: {urban_df.shape}")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据整合测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("regress.py 投资数据功能测试")
    print("=" * 50)
    
    # 显示当前工作目录
    print(f"当前工作目录: {os.getcwd()}")
    
    # 执行测试
    test1 = test_investment_file()
    test2 = test_data_integration()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"  投资文件检查: {'✓ 通过' if test1 else '✗ 失败'}")
    print(f"  数据整合测试: {'✓ 通过' if test2 else '✗ 失败'}")
    
    if test1 and test2:
        print("\n✓ 所有测试通过，可以运行修改后的 regress.py")
        print("  回归模型将包含以下解释变量:")
        print("  1. 基金数量")
        print("  2. 城镇化率")
        print("  3. 固定资产投资")
    else:
        print("\n✗ 部分测试失败，请解决相关问题后再运行 regress.py")

if __name__ == "__main__":
    main()

