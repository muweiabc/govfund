#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OLS回归分析脚本
使用statsmodels进行普通最小二乘回归
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS

def perform_ols_regression():
    """
    执行OLS回归分析
    """
    try:
        print("=== 执行OLS回归分析 ===")
        
        # 1. 读取数据
        print("1. 读取数据...")
        df = pd.read_excel('regress_data_with_gdp.xlsx', sheet_name='回归数据')
        print(f"   - 数据行数: {len(df):,}")
        
        # 2. 创建面板数据结构
        print("2. 创建面板数据结构...")
        
        panel_data = []
        for idx, row in df.iterrows():
            company = row['公司名称']
            investment_year = row['投资年份']
            treatment = row['treatment']
            province = row['省份']
            
            # 前3年数据 (post=0)
            for year_offset in range(1, 4):
                year = investment_year - year_offset
                if year >= 1992:
                    patent_count = row[f'前3年专利数_前{year_offset}年']
                    gdp_value = row[f'前3年GDP_前{year_offset}年']
                    ln_gdp = row[f'ln_前3年GDP_前{year_offset}年']
                    
                    panel_data.append({
                        'company': company,
                        'year': year,
                        'investment_year': investment_year,
                        'treatment': treatment,
                        'post': 0,
                        'patent_count': patent_count,
                        'ln_patent_plus_1': np.log(patent_count + 1),
                        'province': province,
                        'gdp': gdp_value,
                        'ln_gdp': ln_gdp,
                        'time_to_investment': year_offset,
                        'period': 'pre'
                    })
            
            # 后3年数据 (post=1)
            for year_offset in range(1, 4):
                year = investment_year + year_offset
                if year <= 2025:
                    patent_count = row[f'后3年专利数_后{year_offset}年']
                    gdp_value = row[f'后3年GDP_后{year_offset}年']
                    ln_gdp = row[f'ln_后3年GDP_后{year_offset}年']
                    
                    panel_data.append({
                        'company': company,
                        'year': year,
                        'investment_year': investment_year,
                        'treatment': treatment,
                        'post': 1,
                        'patent_count': patent_count,
                        'ln_patent_plus_1': np.log(patent_count + 1),
                        'province': province,
                        'gdp': gdp_value,
                        'ln_gdp': ln_gdp,
                        'time_to_investment': -year_offset,
                        'period': 'post'
                    })
        
        # 3. 创建面板数据框
        print("3. 创建面板数据框...")
        panel_df = pd.DataFrame(panel_data)
        print(f"   - 面板数据行数: {len(panel_df):,}")
        print(f"   - 面板数据列数: {len(panel_df.columns)}")
        
        # 4. 数据统计
        print("4. 面板数据统计...")
        print(f"   - 公司数量: {panel_df['company'].nunique():,}")
        print(f"   - 年份范围: {panel_df['year'].min()} - {panel_df['year'].max()}")
        print(f"   - 投资年份范围: {panel_df['investment_year'].min()} - {panel_df['investment_year'].max()}")
        
        # 按treatment和post分组统计
        group_stats = panel_df.groupby(['treatment', 'post'])['ln_patent_plus_1'].agg(['count', 'mean', 'std']).round(4)
        print(f"\n5. 分组统计:")
        print(group_stats)
        
        # 6. 准备回归变量
        print("\n6. 准备回归变量...")
        
        # 添加交互项
        panel_df['treatment_post'] = panel_df['treatment'] * panel_df['post']
        
        # 选择回归变量
        control_vars = ['treatment', 'post', 'treatment_post', 'ln_gdp']
        
        # 检查数据类型并转换
        print("   - 检查数据类型...")
        for var in control_vars:
            if var in panel_df.columns:
                print(f"     {var}: {panel_df[var].dtype}")
                # 确保数值类型
                if panel_df[var].dtype == 'object':
                    panel_df[var] = pd.to_numeric(panel_df[var], errors='coerce')
                elif panel_df[var].dtype == 'bool':
                    panel_df[var] = panel_df[var].astype(int)
        
        # 检查被解释变量类型
        print(f"     ln_patent_plus_1: {panel_df['ln_patent_plus_1'].dtype}")
        if panel_df['ln_patent_plus_1'].dtype == 'object':
            panel_df['ln_patent_plus_1'] = pd.to_numeric(panel_df['ln_patent_plus_1'], errors='coerce')
        
        # 移除包含NaN的行
        print("   - 移除包含NaN的行...")
        initial_rows = len(panel_df)
        panel_df = panel_df.dropna(subset=control_vars + ['ln_patent_plus_1'])
        final_rows = len(panel_df)
        print(f"     - 初始行数: {initial_rows:,}")
        print(f"     - 最终行数: {final_rows:,}")
        print(f"     - 移除行数: {initial_rows - final_rows:,}")
        
        X = panel_df[control_vars]
        y = panel_df['ln_patent_plus_1']
        
        print(f"   - 回归变量数量: {len(control_vars)}")
        print(f"   - 控制变量: GDP")
        print(f"   - 样本数: {len(panel_df):,}")
        
        # 7. 执行OLS回归
        print("\n7. 执行OLS回归...")
        
        # 检查数据是否为空
        if len(panel_df) == 0:
            print("   ❌ 错误: 处理后没有有效数据")
            return None
        
        # 检查是否有足够的观测值
        if len(panel_df) < len(control_vars) + 1:
            print(f"   ❌ 错误: 观测值数量({len(panel_df)})少于变量数量({len(control_vars) + 1})")
            return None
        
        # 添加常数项
        X_with_constant = sm.add_constant(X)
        
        # 创建OLS模型
        model = OLS(y, X_with_constant)
        results = model.fit()
        
        print("   - 回归完成")
        
        # 8. 显示回归结果
        print("\n8. 回归结果:")
        print("=" * 80)
        print(results.summary())
        print("=" * 80)
        
        # 9. 关键系数解释
        print("\n9. 关键系数解释:")
        if 'treatment' in results.params.index:
            print(f"   - Treatment效应 (β1): {results.params['treatment']:.4f}")
            print(f"     t值: {results.tvalues['treatment']:.4f}, p值: {results.pvalues['treatment']:.4f}")
        
        if 'post' in results.params.index:
            print(f"   - Post效应 (β2): {results.params['post']:.4f}")
            print(f"     t值: {results.tvalues['post']:.4f}, p值: {results.pvalues['post']:.4f}")
        
        print(f"   - DID效应 (β3): {results.params['treatment_post']:.4f}")
        print(f"     t值: {results.tvalues['treatment_post']:.4f}, p值: {results.pvalues['treatment_post']:.4f}")
        
        print(f"   - GDP控制变量 (β4): {results.params['ln_gdp']:.4f}")
        print(f"     t值: {results.tvalues['ln_gdp']:.4f}, p值: {results.pvalues['ln_gdp']:.4f}")
        
        # 10. 模型诊断
        print("\n10. 模型诊断:")
        print(f"   - R²: {results.rsquared:.4f}")
        print(f"   - 调整R²: {results.rsquared_adj:.4f}")
        print(f"   - F统计量: {results.fvalue:.4f}")
        print(f"   - F统计量p值: {results.f_pvalue:.4f}")
        print(f"   - AIC: {results.aic:.4f}")
        print(f"   - BIC: {results.bic:.4f}")
        
        # 11. 计算边际效应
        print(f"\n11. 边际效应分析:")
        # 控制组在投资前后的变化
        control_pre = panel_df[(panel_df['treatment'] == 0) & (panel_df['post'] == 0)]['ln_patent_plus_1'].mean()
        control_post = panel_df[(panel_df['treatment'] == 0) & (panel_df['post'] == 1)]['ln_patent_plus_1'].mean()
        control_change = control_post - control_pre
        
        # 处理组在投资前后的变化
        treatment_pre = panel_df[(panel_df['treatment'] == 1) & (panel_df['post'] == 0)]['ln_patent_plus_1'].mean()
        treatment_post = panel_df[(panel_df['treatment'] == 1) & (panel_df['post'] == 1)]['ln_patent_plus_1'].mean()
        treatment_change = treatment_post - treatment_pre
        
        print(f"   - 控制组投资前平均ln(专利+1): {control_pre:.4f}")
        print(f"   - 控制组投资后平均ln(专利+1): {control_post:.4f}")
        print(f"   - 控制组变化: {control_change:.4f}")
        print(f"   - 处理组投资前平均ln(专利+1): {treatment_pre:.4f}")
        print(f"   - 处理组投资后平均ln(专利+1): {treatment_post:.4f}")
        print(f"   - 处理组变化: {treatment_change:.4f}")
        print(f"   - DID效应 (处理组变化 - 控制组变化): {treatment_change - control_change:.4f}")
        
        # 12. 保存结果
        print("\n12. 保存结果...")
        
        # 保存面板数据
        panel_filename = 'ols_panel_data.xlsx'
        with pd.ExcelWriter(panel_filename, engine='openpyxl') as writer:
            panel_df.to_excel(writer, sheet_name='面板数据', index=False)
            
            # 保存回归结果
            variables = ['常数项', 'Treatment', 'Post', 'Treatment×Post', 'ln(GDP+1)']
            coefficients = [results.params['const'], results.params['treatment'], results.params['post'], 
                          results.params['treatment_post'], results.params['ln_gdp']]
            std_errors = [results.bse['const'], results.bse['treatment'], results.bse['post'], 
                         results.bse['treatment_post'], results.bse['ln_gdp']]
            t_stats = [results.tvalues['const'], results.tvalues['treatment'], results.tvalues['post'], 
                      results.tvalues['treatment_post'], results.tvalues['ln_gdp']]
            p_values = [results.pvalues['const'], results.pvalues['treatment'], results.pvalues['post'], 
                       results.pvalues['treatment_post'], results.pvalues['ln_gdp']]
            
            results_summary = pd.DataFrame({
                '变量': variables,
                '系数': coefficients,
                '标准误': std_errors,
                't值': t_stats,
                'p值': p_values
            })
            results_summary.to_excel(writer, sheet_name='回归结果', index=False)
            
            # 保存分组统计
            group_stats.to_excel(writer, sheet_name='分组统计')
            
            # 保存GDP统计
            gdp_stats = panel_df[['gdp', 'ln_gdp']].describe()
            gdp_stats.to_excel(writer, sheet_name='GDP统计')
            
            # 保存模型诊断统计
            model_stats = pd.DataFrame({
                '统计量': ['R²', '调整R²', 'F统计量', 'F统计量p值', 'AIC', 'BIC'],
                '值': [results.rsquared, results.rsquared_adj, results.fvalue, results.f_pvalue, results.aic, results.bic]
            })
            model_stats.to_excel(writer, sheet_name='模型诊断', index=False)
        
        print(f"   - 结果已保存: {panel_filename}")
        
        return {
            'panel_df': panel_df,
            'regression_results': results,
            'did_effect': results.params['treatment_post'],
            'did_t_value': results.tvalues['treatment_post'],
            'did_p_value': results.pvalues['treatment_post'],
            'gdp_effect': results.params['ln_gdp'],
            'r_squared': results.rsquared,
            'adj_r_squared': results.rsquared_adj
        }
        
    except Exception as e:
        print(f"执行OLS回归时出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 执行OLS回归分析
    result = perform_ols_regression()
    
    if result:
        print(f"\n=== OLS回归分析完成 ===")
        print(f"DID效应系数: {result['did_effect']:.4f}")
        print(f"t值: {result['did_t_value']:.4f}")
        print(f"p值: {result['did_p_value']:.4f}")
        print(f"GDP控制变量系数: {result['gdp_effect']:.4f}")
        print(f"R²: {result['r_squared']:.4f}")
        print(f"调整R²: {result['adj_r_squared']:.4f}")
        
        if result['did_p_value'] < 0.05:
            print("✅ DID效应在5%水平上显著")
        elif result['did_p_value'] < 0.1:
            print("⚠️ DID效应在10%水平上显著")
        else:
            print("❌ DID效应不显著")
        
    else:
        print("回归分析失败")
