#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
regress.py 功能测试脚本
用于验证回归分析功能
"""

import pandas as pd
import os
import traceback

def test_data_compatibility():
    """测试数据兼容性"""
    print("=== 测试数据兼容性 ===")
    
    # 测试GDP数据
    print("\n1. 测试GDP数据...")
    try:
        gdp_df = pd.read_excel('gdp.xlsx')
        print(f"  ✓ GDP数据读取成功")
        print(f"    数据形状: {gdp_df.shape}")
        print(f"    列名: {list(gdp_df.columns)}")
        
        # 检查必要列
        required_cols = ['年份', '省级', '人均地区生产总值/元']
        missing_cols = [col for col in required_cols if col not in gdp_df.columns]
        if missing_cols:
            print(f"  ✗ 缺少必要列: {missing_cols}")
            return False
        else:
            print(f"  ✓ 所有必要列都存在")
        
        # 检查数据类型
        print(f"    年份列类型: {gdp_df['年份'].dtype}")
        print(f"    省级列类型: {gdp_df['省级'].dtype}")
        print(f"    人均GDP列类型: {gdp_df['人均地区生产总值/元'].dtype}")
        
        # 检查数据范围
        print(f"    年份范围: {gdp_df['年份'].min()} - {gdp_df['年份'].max()}")
        print(f"    省份数量: {gdp_df['省级'].nunique()}")
        print(f"    省份列表: {sorted(gdp_df['省级'].unique())}")
        
    except Exception as e:
        print(f"  ✗ GDP数据测试失败: {e}")
        return False
    
    # 测试基金数据
    print("\n2. 测试基金数据...")
    try:
        fund_df = pd.read_excel('govfund_analysis_results.xlsx')
        print(f"  ✓ 基金数据读取成功")
        print(f"    数据形状: {fund_df.shape}")
        print(f"    列名: {list(fund_df.columns)}")
        
        # 检查必要列
        required_cols = ['省份', '成立年份', '基金数量']
        missing_cols = [col for col in required_cols if col not in fund_df.columns]
        if missing_cols:
            print(f"  ✗ 缺少必要列: {missing_cols}")
            return False
        else:
            print(f"  ✓ 所有必要列都存在")
        
        # 检查数据类型
        print(f"    省份列类型: {fund_df['省份'].dtype}")
        print(f"    成立年份列类型: {fund_df['成立年份'].dtype}")
        print(f"    基金数量列类型: {fund_df['基金数量'].dtype}")
        
        # 检查数据范围
        print(f"    年份范围: {fund_df['成立年份'].min()} - {fund_df['成立年份'].max()}")
        print(f"    省份数量: {fund_df['省份'].nunique()}")
        print(f"    省份列表: {sorted(fund_df['省份'].unique())}")
        
    except Exception as e:
        print(f"  ✗ 基金数据测试失败: {e}")
        return False
    
    return True

def test_data_matching():
    """测试数据匹配情况"""
    print("\n=== 测试数据匹配情况 ===")
    
    try:
        gdp_df = pd.read_excel('gdp.xlsx')
        fund_df = pd.read_excel('govfund_analysis_results.xlsx')
        
        # 筛选2000年后的数据
        gdp_filtered = gdp_df[gdp_df['年份'] > 2000].copy()
        print(f"GDP数据中2000年后的记录数: {len(gdp_filtered)}")
        
        # 检查匹配情况
        matched_count = 0
        unmatched_count = 0
        match_details = []
        
        for idx, row in gdp_filtered.iterrows():
            province = row['省级']
            year = row['年份']
            
            # 在基金数据中查找匹配
            fund_match = fund_df[(fund_df['省份'] == province) & (fund_df['成立年份'] == year)]
            
            if len(fund_match) > 0:
                matched_count += 1
                fund_count = fund_match.iloc[0]['基金数量']
                match_details.append(f"{province}-{year}: {fund_count}个基金")
            else:
                unmatched_count += 1
        
        print(f"匹配记录数: {matched_count}")
        print(f"未匹配记录数: {unmatched_count}")
        print(f"匹配率: {matched_count/(matched_count+unmatched_count)*100:.1f}%")
        
        if matched_count > 0:
            print("\n匹配详情 (前10个):")
            for detail in match_details[:10]:
                print(f"  {detail}")
        
        if unmatched_count > 0:
            print(f"\n未匹配的省份-年份组合 (前10个):")
            unmatched_examples = []
            for idx, row in gdp_filtered.iterrows():
                province = row['省级']
                year = row['年份']
                fund_match = fund_df[(fund_df['省份'] == province) & (fund_df['成立年份'] == year)]
                if len(fund_match) == 0:
                    unmatched_examples.append(f"{province}-{year}")
                    if len(unmatched_examples) >= 10:
                        break
            
            for example in unmatched_examples:
                print(f"  {example}")
        
        return matched_count > 0
        
    except Exception as e:
        print(f"✗ 数据匹配测试失败: {e}")
        traceback.print_exc()
        return False

def test_linearmodels():
    """测试linearmodels库"""
    print("\n=== 测试linearmodels库 ===")
    
    try:
        import linearmodels
        print(f"✓ linearmodels库导入成功")
        print(f"  版本: {linearmodels.__version__}")
        return True
    except ImportError:
        print("✗ linearmodels库未安装")
        print("  请运行: pip install linearmodels")
        return False
    except Exception as e:
        print(f"✗ linearmodels库测试失败: {e}")
        return False

def main():
    """主函数"""
    print("regress.py 功能测试")
    print("=" * 50)
    
    # 显示当前工作目录
    print(f"当前工作目录: {os.getcwd()}")
    
    # 检查文件
    required_files = ['gdp.xlsx', 'govfund_analysis_results.xlsx']
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
        return
    
    print("\n" + "=" * 50)
    
    # 执行测试
    test1 = test_data_compatibility()
    test2 = test_data_matching()
    test3 = test_linearmodels()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"  数据兼容性: {'✓ 通过' if test1 else '✗ 失败'}")
    print(f"  数据匹配: {'✓ 通过' if test2 else '✗ 失败'}")
    print(f"  库依赖: {'✓ 通过' if test3 else '✗ 失败'}")
    
    if test1 and test2 and test3:
        print("\n✓ 所有测试通过，可以运行 regress.py")
    else:
        print("\n✗ 部分测试失败，请解决相关问题后再运行 regress.py")
        
        if not test1:
            print("  - 检查数据文件格式和列名")
        if not test2:
            print("  - 检查年份和省份名称是否一致")
        if not test3:
            print("  - 安装linearmodels库: pip install linearmodels")

if __name__ == "__main__":
    main()
