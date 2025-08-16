#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多重共线性检查脚本
用于诊断DID回归中的多重共线性问题
"""

import pandas as pd
import numpy as np
from scipy import stats

def check_multicollinearity(X, variable_names=None):
    """
    检查回归变量之间的多重共线性
    
    参数:
    X: 回归变量矩阵
    variable_names: 变量名称列表
    
    返回:
    VIF值字典和相关性矩阵
    """
    if variable_names is None:
        variable_names = [f'Var_{i}' for i in range(X.shape[1])]
    
    print("=== 多重共线性检查 ===")
    
    # 1. 计算相关性矩阵
    print("\n1. 相关性矩阵:")
    corr_matrix = np.corrcoef(X.T)
    corr_df = pd.DataFrame(corr_matrix, columns=variable_names, index=variable_names)
    print(corr_df.round(3))
    
    # 2. 检查高相关性
    print("\n2. 高相关性检查 (|r| > 0.8):")
    high_corr_pairs = []
    for i in range(len(variable_names)):
        for j in range(i+1, len(variable_names)):
            corr_val = corr_matrix[i, j]
            if abs(corr_val) > 0.8:
                high_corr_pairs.append((variable_names[i], variable_names[j], corr_val))
                print(f"   {variable_names[i]} vs {variable_names[j]}: r = {corr_val:.3f}")
    
    if not high_corr_pairs:
        print("   ✅ 没有发现高相关性变量对")
    
    # 3. 计算VIF (Variance Inflation Factor)
    print("\n3. VIF值检查:")
    vif_values = {}
    
    for i in range(X.shape[1]):
        # 将第i个变量作为因变量，其他变量作为自变量
        y_temp = X[:, i]
        X_temp = np.delete(X, i, axis=1)
        
        # 添加常数项
        X_temp_with_const = np.column_stack([np.ones(X_temp.shape[0]), X_temp])
        
        try:
            # 计算R²
            beta = np.linalg.lstsq(X_temp_with_const, y_temp, rcond=None)[0]
            y_pred = X_temp_with_const @ beta
            ss_res = np.sum((y_temp - y_pred) ** 2)
            ss_tot = np.sum((y_temp - np.mean(y_temp)) ** 2)
            r_squared = 1 - (ss_res / ss_tot)
            
            # 计算VIF
            vif = 1 / (1 - r_squared) if r_squared < 1 else float('inf')
            vif_values[variable_names[i]] = vif
            
            status = "⚠️" if vif > 10 else "✅"
            print(f"   {status} {variable_names[i]}: VIF = {vif:.2f}")
            
        except:
            vif_values[variable_names[i]] = float('inf')
            print(f"   ❌ {variable_names[i]}: VIF = ∞ (计算失败)")
    
    # 4. 多重共线性诊断
    print("\n4. 多重共线性诊断:")
    high_vif_vars = [var for var, vif in vif_values.items() if vif > 10]
    
    if high_vif_vars:
        print(f"   ❌ 发现高VIF变量 (VIF > 10): {', '.join(high_vif_vars)}")
        print("   建议:")
        print("   - 检查虚拟变量设置，确保排除基准类别")
        print("   - 避免同时使用年份虚拟变量和time_effects")
        print("   - 考虑删除高度相关的变量")
    else:
        print("   ✅ 没有发现严重的多重共线性问题")
    
    # 5. 条件数检查
    print("\n5. 条件数检查:")
    try:
        # 标准化数据
        X_centered = X - np.mean(X, axis=0)
        X_scaled = X_centered / np.std(X, axis=0)
        
        # 计算条件数
        eigenvals = np.linalg.eigvals(X_scaled.T @ X_scaled)
        condition_number = np.sqrt(np.max(eigenvals) / np.min(eigenvals))
        
        print(f"   条件数: {condition_number:.2f}")
        
        if condition_number > 30:
            print("   ⚠️ 条件数较高，可能存在多重共线性")
        else:
            print("   ✅ 条件数正常")
            
    except Exception as e:
        print(f"   ❌ 条件数计算失败: {e}")
    
    return vif_values, corr_df

def diagnose_did_data():
    """
    诊断DID数据中的潜在问题
    """
    print("=== DID数据诊断 ===")
    
    try:
        # 读取数据
        df = pd.read_excel('regress_data_with_gdp.xlsx', sheet_name='回归数据')
        print(f"✅ 成功读取数据，共 {len(df):,} 行")
        
        # 检查关键变量
        key_vars = ['公司名称', '投资年份', 'treatment', '省份']
        missing_vars = [var for var in key_vars if var not in df.columns]
        
        if missing_vars:
            print(f"❌ 缺少关键变量: {missing_vars}")
            return
        
        print("✅ 所有关键变量都存在")
        
        # 检查treatment变量
        print(f"\nTreatment变量分布:")
        print(df['treatment'].value_counts())
        
        # 检查投资年份分布
        print(f"\n投资年份分布:")
        year_counts = df['投资年份'].value_counts().sort_index()
        print(year_counts.head(10))
        print("...")
        print(year_counts.tail(10))
        
        # 检查省份分布
        print(f"\n省份分布 (前10个):")
        province_counts = df['省份'].value_counts().head(10)
        print(province_counts)
        
        # 检查专利数据列
        patent_cols = [col for col in df.columns if '专利数' in col]
        print(f"\n专利数据列: {len(patent_cols)} 个")
        
        # 检查GDP数据列
        gdp_cols = [col for col in df.columns if 'GDP' in col]
        print(f"GDP数据列: {len(gdp_cols)} 个")
        
        # 检查数据质量
        print(f"\n数据质量检查:")
        print(f"   - 投资年份缺失值: {df['投资年份'].isna().sum()}")
        print(f"   - 省份缺失值: {df['省份'].isna().sum()}")
        print(f"   - treatment缺失值: {df['treatment'].isna().sum()}")
        
        # 检查专利数据是否有负值
        for col in patent_cols:
            if col in df.columns:
                neg_count = (df[col] < 0).sum()
                if neg_count > 0:
                    print(f"   ⚠️ {col} 有 {neg_count} 个负值")
        
    except Exception as e:
        print(f"❌ 数据诊断失败: {e}")

if __name__ == "__main__":
    # 运行数据诊断
    diagnose_did_data()
    
    print("\n" + "="*60)
    print("多重共线性检查完成")
    print("="*60)
    print("\n如果发现多重共线性问题，建议:")
    print("1. 检查虚拟变量设置，确保排除基准类别")
    print("2. 避免同时使用年份虚拟变量和time_effects")
    print("3. 检查变量之间的逻辑关系")
    print("4. 考虑使用正则化方法或主成分分析")
