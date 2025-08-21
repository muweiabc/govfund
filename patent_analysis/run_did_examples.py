#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DID回归示例脚本
展示如何使用不同的参数组合运行DID回归
"""

from did import (
    perform_did_regression_with_gdp,
    perform_did_regression_with_year_dummies
)

def run_did_examples():
    """
    运行不同配置的DID回归示例
    """
    print("=== DID回归示例运行 ===")
    
    # 示例1: 基础DID回归（只包含GDP控制变量）
    print("\n" + "="*60)
    print("示例1: 基础DID回归（只包含GDP控制变量）")
    print("="*60)
    
    result1 = perform_did_regression_with_gdp(
        enable_province_dummies=False,  # 禁用省份虚拟变量
        enable_time_dummies=False       # 禁用时间虚拟变量
    )
    
    if result1:
        print(f"✅ 基础DID回归完成")
        print(f"   DID效应系数: {result1['did_effect']:.4f}")
        print(f"   t值: {result1['did_t_value']:.4f}")
        print(f"   p值: {result1['did_p_value']:.4f}")
        print(f"   省份虚拟变量数量: {result1['province_dummy_count']}")
    else:
        print("❌ 基础DID回归失败")
    
    # 示例2: 带省份虚拟变量的DID回归
    print("\n" + "="*60)
    print("示例2: 带省份虚拟变量的DID回归")
    print("="*60)
    
    result2 = perform_did_regression_with_gdp(
        enable_province_dummies=True,   # 启用省份虚拟变量
        enable_time_dummies=False       # 禁用时间虚拟变量
    )
    
    if result2:
        print(f"✅ 带省份虚拟变量的DID回归完成")
        print(f"   DID效应系数: {result2['did_effect']:.4f}")
        print(f"   t值: {result2['did_t_value']:.4f}")
        print(f"   p值: {result2['did_p_value']:.4f}")
        print(f"   省份虚拟变量数量: {result2['province_dummy_count']}")
    else:
        print("❌ 带省份虚拟变量的DID回归失败")
    
    # 示例3: 带年份虚拟变量的DID回归
    print("\n" + "="*60)
    print("示例3: 带年份虚拟变量的DID回归")
    print("="*60)
    
    result3 = perform_did_regression_with_year_dummies(
        enable_province_dummies=False,  # 禁用省份虚拟变量
        enable_time_dummies=True        # 启用年份虚拟变量
    )
    
    if result3:
        print(f"✅ 带年份虚拟变量的DID回归完成")
        print(f"   DID效应系数: {result3['did_effect']:.4f}")
        print(f"   t值: {result3['did_t_value']:.4f}")
        print(f"   p值: {result3['did_p_value']:.4f}")
        print(f"   年份虚拟变量数量: {result3['year_dummy_count']}")
        print(f"   省份虚拟变量数量: {result3['province_dummy_count']}")
    else:
        print("❌ 带年份虚拟变量的DID回归失败")
    
    # 示例4: 完整DID回归（包含年份和省份虚拟变量）
    print("\n" + "="*60)
    print("示例4: 完整DID回归（包含年份和省份虚拟变量）")
    print("="*60)
    
    result4 = perform_did_regression_with_year_dummies(
        enable_province_dummies=True,   # 启用省份虚拟变量
        enable_time_dummies=True        # 启用年份虚拟变量
    )
    
    if result4:
        print(f"✅ 完整DID回归完成")
        print(f"   DID效应系数: {result4['did_effect']:.4f}")
        print(f"   t值: {result4['did_t_value']:.4f}")
        print(f"   p值: {result4['did_p_value']:.4f}")
        print(f"   年份虚拟变量数量: {result4['year_dummy_count']}")
        print(f"   省份虚拟变量数量: {result4['province_dummy_count']}")
        print(f"   显著的年份虚拟变量: {result4['significant_year_dummies']}")
        print(f"   显著的省份虚拟变量: {result4['significant_province_dummies']}")
    else:
        print("❌ 完整DID回归失败")
    
    print("\n" + "="*60)
    print("所有示例运行完成")
    print("="*60)

if __name__ == "__main__":
    run_did_examples()
