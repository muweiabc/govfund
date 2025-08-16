#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列秩问题诊断脚本
用于诊断DID回归中的"exog does not have full column rank"错误
"""

import pandas as pd
import numpy as np
from scipy import linalg

def check_matrix_rank(X, variable_names=None):
    """
    检查矩阵的列秩
    
    参数:
    X: 回归变量矩阵
    variable_names: 变量名称列表
    
    返回:
    秩信息和建议
    """
    if variable_names is None:
        variable_names = [f'Var_{i}' for i in range(X.shape[1])]
    
    print("=== 矩阵列秩检查 ===")
    print(f"矩阵形状: {X.shape}")
    
    # 1. 检查矩阵秩
    rank = np.linalg.matrix_rank(X)
    print(f"矩阵秩: {rank}")
    print(f"列数: {X.shape[1]}")
    
    if rank < X.shape[1]:
        print(f"❌ 列秩不足！秩({rank}) < 列数({X.shape[1]})")
        print("   这会导致 'exog does not have full column rank' 错误")
    else:
        print("✅ 矩阵列秩正常")
        return
    
    # 2. 检查每列是否全为0
    print("\n2. 检查零列:")
    zero_cols = []
    for i, name in enumerate(variable_names):
        if np.all(X[:, i] == 0):
            zero_cols.append((i, name))
            print(f"   ❌ 第{i}列 '{name}' 全为0")
    
    if not zero_cols:
        print("   ✅ 没有发现零列")
    
    # 3. 检查常数列
    print("\n3. 检查常数列:")
    const_cols = []
    for i, name in enumerate(variable_names):
        if np.all(X[:, i] == X[0, i]):
            const_cols.append((i, name, X[0, i]))
            print(f"   ❌ 第{i}列 '{name}' 为常数: {X[0, i]}")
    
    if not const_cols:
        print("   ✅ 没有发现常数列")
    
    # 4. 检查线性相关性
    print("\n4. 检查线性相关性:")
    try:
        # 计算相关系数矩阵
        corr_matrix = np.corrcoef(X.T)
        
        # 寻找完全相关的变量对
        perfect_corr_pairs = []
        for i in range(len(variable_names)):
            for j in range(i+1, len(variable_names)):
                corr_val = corr_matrix[i, j]
                if abs(corr_val) > 0.999:  # 几乎完全相关
                    perfect_corr_pairs.append((variable_names[i], variable_names[j], corr_val))
                    print(f"   ❌ {variable_names[i]} vs {variable_names[j]}: r = {corr_val:.6f}")
        
        if not perfect_corr_pairs:
            print("   ✅ 没有发现完全相关的变量对")
            
    except Exception as e:
        print(f"   ❌ 相关性检查失败: {e}")
    
    # 5. 奇异值分解分析
    print("\n5. 奇异值分析:")
    try:
        U, s, Vt = linalg.svd(X)
        print(f"   奇异值: {s[:10]}...")  # 显示前10个奇异值
        
        # 检查接近0的奇异值
        small_singular_values = s[s < 1e-10]
        if len(small_singular_values) > 0:
            print(f"   ⚠️ 发现 {len(small_singular_values)} 个接近0的奇异值")
            print(f"   最小奇异值: {np.min(s):.2e}")
        else:
            print("   ✅ 奇异值正常")
            
    except Exception as e:
        print(f"   ❌ 奇异值分解失败: {e}")
    
    # 6. 提供解决方案
    print("\n6. 解决方案建议:")
    if zero_cols:
        print("   - 删除全为0的列")
    if const_cols:
        print("   - 删除常数列")
    if perfect_corr_pairs:
        print("   - 删除高度相关的变量之一")
    print("   - 检查虚拟变量设置，确保排除基准类别")
    print("   - 避免同时使用年份虚拟变量和time_effects")
    print("   - 检查treatment和post变量的分布")

def diagnose_did_panel_data():
    """
    诊断DID面板数据中的潜在问题
    """
    print("=== DID面板数据诊断 ===")
    
    try:
        # 读取数据
        df = pd.read_excel('regress_data_with_gdp.xlsx', sheet_name='回归数据')
        print(f"✅ 成功读取数据，共 {len(df):,} 行")
        
        # 创建面板数据结构（模拟DID回归中的数据处理）
        print("\n创建面板数据结构...")
        
        panel_data = []
        for idx, row in df.head(100).iterrows():  # 只处理前100行作为示例
            company = row['公司名称']
            investment_year = row['投资年份']
            treatment = row['treatment']
            province = row['省份']
            
            # 前3年数据
            for year_offset in range(1, 4):
                year = investment_year - year_offset
                if year >= 1992:
                    panel_data.append({
                        'company': company,
                        'year': year,
                        'investment_year': investment_year,
                        'treatment': treatment,
                        'post': 0,
                        'province': province
                    })
            
            # 投资当年
            panel_data.append({
                'company': company,
                'year': investment_year,
                'investment_year': investment_year,
                'treatment': treatment,
                'post': 0,
                'province': province
            })
            
            # 后3年数据
            for year_offset in range(1, 4):
                year = investment_year + year_offset
                if year <= 2025:
                    panel_data.append({
                        'company': company,
                        'year': year,
                        'investment_year': investment_year,
                        'treatment': treatment,
                        'post': 1,
                        'province': province
                    })
        
        panel_df = pd.DataFrame(panel_data)
        print(f"面板数据行数: {len(panel_df):,}")
        
        # 检查关键变量的分布
        print(f"\n关键变量分布:")
        print(f"   - treatment: {panel_df['treatment'].value_counts().to_dict()}")
        print(f"   - post: {panel_df['post'].value_counts().to_dict()}")
        print(f"   - 省份数量: {panel_df['province'].nunique()}")
        print(f"   - 年份范围: {panel_df['year'].min()} - {panel_df['year'].max()}")
        
        # 检查treatment_post交互项
        panel_df['treatment_post'] = panel_df['treatment'] * panel_df['post']
        print(f"   - treatment_post: {panel_df['treatment_post'].value_counts().to_dict()}")
        
        # 检查是否有某些组合的观测值为0
        print(f"\n变量组合检查:")
        for treatment_val in [0, 1]:
            for post_val in [0, 1]:
                count = len(panel_df[(panel_df['treatment'] == treatment_val) & (panel_df['post'] == post_val)])
                print(f"   - treatment={treatment_val}, post={post_val}: {count} 个观测值")
        
        # 检查省份虚拟变量
        print(f"\n省份虚拟变量检查:")
        provinces = sorted(panel_df['province'].unique())
        for i, province in enumerate(provinces[:5]):  # 只检查前5个省份
            count = len(panel_df[panel_df['province'] == province])
            print(f"   - {province}: {count} 个观测值")
        
        # 检查年份虚拟变量
        print(f"\n年份虚拟变量检查:")
        years = sorted(panel_df['year'].unique())
        for year in years[:5]:  # 只检查前5个年份
            count = len(panel_df[panel_df['year'] == year])
            print(f"   - {year}年: {count} 个观测值")
        
        return panel_df
        
    except Exception as e:
        print(f"❌ 数据诊断失败: {e}")
        return None

def test_regression_matrix():
    """
    测试回归矩阵的构建
    """
    print("\n=== 测试回归矩阵构建 ===")
    
    panel_df = diagnose_did_panel_data()
    if panel_df is None:
        return
    
    try:
        # 设置面板数据索引
        panel_df = panel_df.set_index(['company', 'year'])
        
        # 创建虚拟变量
        print("\n创建虚拟变量...")
        
        # 省份虚拟变量
        provinces = sorted(panel_df['province'].unique())
        base_province = provinces[0]
        print(f"基准省份: {base_province}")
        
        for province in provinces[1:]:
            panel_df[f'province_{province}'] = (panel_df['province'] == province).astype(int)
        
        province_dummy_cols = [col for col in panel_df.columns if col.startswith('province_')]
        print(f"省份虚拟变量数量: {len(province_dummy_cols)}")
        
        # 年份虚拟变量
        years = sorted(panel_df['year'].unique())
        base_year = years[0]
        print(f"基准年份: {base_year}")
        
        for year in years[1:]:
            panel_df[f'year_{year}'] = (panel_df['year'] == year).astype(int)
        
        year_dummy_cols = [col for col in panel_df.columns if col.startswith('year_')]
        print(f"年份虚拟变量数量: {len(year_dummy_cols)}")
        
        # 构建回归矩阵
        print("\n构建回归矩阵...")
        
        # 基础变量
        control_vars = ['treatment', 'post', 'treatment_post']
        
        # 添加省份虚拟变量
        control_vars += province_dummy_cols
        
        # 添加年份虚拟变量
        control_vars += year_dummy_cols
        
        print(f"回归变量: {control_vars}")
        
        # 检查变量是否存在
        missing_vars = [var for var in control_vars if var not in panel_df.columns]
        if missing_vars:
            print(f"❌ 缺少变量: {missing_vars}")
            return
        
        # 构建X矩阵
        X = panel_df[control_vars].values
        variable_names = control_vars
        
        print(f"X矩阵形状: {X.shape}")
        
        # 检查矩阵秩
        check_matrix_rank(X, variable_names)
        
        # 检查每列的基本统计
        print(f"\n变量基本统计:")
        for i, name in enumerate(variable_names):
            col_data = X[:, i]
            print(f"   {name}: 均值={np.mean(col_data):.3f}, 标准差={np.std(col_data):.3f}, "
                  f"最小值={np.min(col_data):.3f}, 最大值={np.max(col_data):.3f}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行诊断
    test_regression_matrix()
    
    print("\n" + "="*60)
    print("列秩问题诊断完成")
    print("="*60)
