#!/usr/bin/env python3
"""
创建增强的回归数据表
从invest中读取投资事件，扩展为前三年和后三年的6行数据，并添加专利数据和其他控制变量
"""

import pandas as pd
import numpy as np
import argparse
from datetime import datetime
import os

def load_patent_data(patent_file='patent_analysis/company_patent_yearly.xlsx'):
    """
    加载专利数据
    """
    print("加载专利数据...")
    
    try:
        # 尝试加载专利数量数据
        patent_count_df = pd.read_excel(patent_file, sheet_name='专利数量', index_col=0)
        print(f"   - 专利数量数据: {patent_count_df.shape}")
        
        # 尝试加载被引证次数数据
        citation_df = pd.read_excel(patent_file, sheet_name='被引证次数', index_col=0)
        print(f"   - 被引证次数数据: {citation_df.shape}")
        
        # 尝试加载发明数量数据
        invention_df = pd.read_excel(patent_file, sheet_name='发明数量', index_col=0)
        print(f"   - 发明数量数据: {invention_df.shape}")
        
        # 尝试加载发明被引证次数数据
        invention_citation_df = pd.read_excel(patent_file, sheet_name='发明被引证次数', index_col=0)
        print(f"   - 发明被引证次数数据: {invention_citation_df.shape}")
        
        return {
            'patent_count': patent_count_df,
            'citation_count': citation_df,
            'invention_count': invention_df,
            'invention_citation': invention_citation_df
        }
        
    except Exception as e:
        print(f"   - 专利数据加载失败: {e}")
        return None

def load_control_variables():
    """
    加载控制变量数据
    """
    print("加载控制变量数据...")
    
    control_data = {}
    
    # 1. GDP数据
    try:
        gdp_df = pd.read_excel('gdp.xlsx')
        print(f"   - GDP数据: {gdp_df.shape}")
        control_data['gdp'] = gdp_df
    except Exception as e:
        print(f"   - GDP数据加载失败: {e}")
    
    # 2. 城镇化率数据
    try:
        urban_df = pd.read_excel('中国城镇化率1990-2023年.xlsx')
        print(f"   - 城镇化率数据: {urban_df.shape}")
        control_data['urban'] = urban_df
    except Exception as e:
        print(f"   - 城镇化率数据加载失败: {e}")
    
    # 3. 固定资产投资数据
    try:
        invest_df = pd.read_excel('2003-2023各省分行业全社会固定资产投资额.xlsx')
        print(f"   - 固定资产投资数据: {invest_df.shape}")
        control_data['fixed_invest'] = invest_df
    except Exception as e:
        print(f"   - 固定资产投资数据加载失败: {e}")
    
    # 4. 就业数据
    try:
        employment_df = pd.read_excel('就业人口.xlsx')
        print(f"   - 就业数据: {employment_df.shape}")
        control_data['employment'] = employment_df
    except Exception as e:
        print(f"   - 就业数据加载失败: {e}")
    
    return control_data

def add_patent_data(panel_df, patent_data):
    """
    为面板数据添加专利信息
    """
    print("添加专利数据...")
    
    if patent_data is None:
        print("   - 无专利数据，跳过")
        return panel_df
    
    # 初始化专利相关列
    panel_df['patent_count'] = 0
    panel_df['citation_count'] = 0
    panel_df['invention_count'] = 0
    panel_df['invention_citation'] = 0
    panel_df['ln_patent_count_plus_1'] = 0
    panel_df['ln_citation_count_plus_1'] = 0
    panel_df['ln_invention_count_plus_1'] = 0
    panel_df['ln_invention_citation_plus_1'] = 0
    
    matched_count = 0
    total_attempts = 0
    
    for idx, row in panel_df.iterrows():
        company = row['company']
        year = row['year']
        
        total_attempts += 1
        
        # 添加专利数量
        if company in patent_data['patent_count'].index:
            year_col = f'y{year}'
            if year_col in patent_data['patent_count'].columns:
                patent_count = patent_data['patent_count'].loc[company, year_col]
                panel_df.at[idx, 'patent_count'] = patent_count
                panel_df.at[idx, 'ln_patent_count_plus_1'] = np.log(patent_count + 1)
                matched_count += 1
        
        # 添加被引证次数
        if company in patent_data['citation_count'].index:
            year_col = f'y{year}'
            if year_col in patent_data['citation_count'].columns:
                citation_count = patent_data['citation_count'].loc[company, year_col]
                panel_df.at[idx, 'citation_count'] = citation_count
                panel_df.at[idx, 'ln_citation_count_plus_1'] = np.log(citation_count + 1)
        
        # 添加发明数量
        if company in patent_data['invention_count'].index:
            year_col = f'y{year}'
            if year_col in patent_data['invention_count'].columns:
                invention_count = patent_data['invention_count'].loc[company, year_col]
                panel_df.at[idx, 'invention_count'] = invention_count
                panel_df.at[idx, 'ln_invention_count_plus_1'] = np.log(invention_count + 1)
        
        # 添加发明被引证次数
        if company in patent_data['invention_citation'].index:
            year_col = f'y{year}'
            if year_col in patent_data['invention_citation'].columns:
                invention_citation = patent_data['invention_citation'].loc[company, year_col]
                panel_df.at[idx, 'invention_citation'] = invention_citation
                panel_df.at[idx, 'ln_invention_citation_plus_1'] = np.log(invention_citation + 1)
        
        # 显示进度
        if (idx + 1) % 5000 == 0:
            print(f"   - 已处理 {idx + 1:,} 条记录...")
    
    print(f"   - 专利数据匹配率: {matched_count / total_attempts * 100:.2f}%")
    return panel_df

def add_control_variables(panel_df, control_data):
    """
    为面板数据添加控制变量
    """
    print("添加控制变量...")
    
    # 初始化控制变量列
    panel_df['gdp'] = 0
    panel_df['ln_gdp'] = 0
    panel_df['urban_rate'] = 0
    panel_df['ln_urban_rate'] = 0
    panel_df['fixed_investment'] = 0
    panel_df['ln_fixed_investment'] = 0
    panel_df['secondary_industry_ratio'] = 0
    panel_df['secondary_employment_ratio'] = 0
    
    # 添加GDP数据
    if 'gdp' in control_data:
        gdp_df = control_data['gdp']
        for idx, row in panel_df.iterrows():
            province = row['province']
            year = row['year']
            
            # 查找匹配的GDP数据
            gdp_match = gdp_df[(gdp_df['省级'] == province) & (gdp_df['年份'] == year)]
            if not gdp_match.empty:
                gdp_value = gdp_match['地区生产总值/亿元'].iloc[0]
                if pd.notna(gdp_value) and gdp_value > 0:
                    panel_df.at[idx, 'gdp'] = gdp_value
                    panel_df.at[idx, 'ln_gdp'] = np.log(gdp_value + 1)
    
    # 添加城镇化率数据
    if 'urban' in control_data:
        urban_df = control_data['urban']
        for idx, row in panel_df.iterrows():
            province = row['province']
            year = row['year']
            
            # 查找匹配的城镇化率数据
            urban_match = urban_df[(urban_df['省份'] == province) & (urban_df['年份'] == year)]
            if not urban_match.empty:
                urban_value = urban_match['城镇化率(%)'].iloc[0]
                if pd.notna(urban_value) and urban_value > 0:
                    panel_df.at[idx, 'urban_rate'] = urban_value / 100  # 转换为小数
                    panel_df.at[idx, 'ln_urban_rate'] = np.log(urban_value / 100 + 1)
    
    print("   - 控制变量添加完成")
    return panel_df

def create_enhanced_regression_data(input_file='invest.xlsx', 
                                  sheet_name='有专利公司首次投资',
                                  patent_file='patent_analysis/company_patent_yearly.xlsx',
                                  output_file='patent_analysis/enhanced_regression_panel_data.xlsx'):
    """
    创建增强的回归面板数据
    """
    print("=== 创建增强的回归面板数据 ===")
    
    # 1. 创建基础面板数据
    print("1. 创建基础面板数据...")
    from create_regression_data import create_regression_data
    
    panel_df = create_regression_data(input_file, sheet_name, 'temp_panel_data.xlsx')
    
    # 2. 加载专利数据
    patent_data = load_patent_data(patent_file)
    
    # 3. 加载控制变量
    control_data = load_control_variables()
    
    # 4. 添加专利数据
    panel_df = add_patent_data(panel_df, patent_data)
    
    # 5. 添加控制变量
    panel_df = add_control_variables(panel_df, control_data)
    
    # 6. 创建虚拟变量
    print("6. 创建虚拟变量...")
    
    # 省份虚拟变量
    province_dummies = pd.get_dummies(panel_df['province'], prefix='province', drop_first=True)
    panel_df = pd.concat([panel_df, province_dummies], axis=1)
    
    # 投资阶段虚拟变量
    stage_dummies = pd.get_dummies(panel_df['investment_stage'], prefix='stage', drop_first=True)
    panel_df = pd.concat([panel_df, stage_dummies], axis=1)
    
    # 年份虚拟变量
    year_dummies = pd.get_dummies(panel_df['year'], prefix='year', drop_first=True)
    panel_df = pd.concat([panel_df, year_dummies], axis=1)
    
    print(f"   - 总列数: {panel_df.shape[1]}")
    
    # 7. 保存数据
    print("7. 保存数据...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 保存面板数据
        panel_df.to_excel(writer, sheet_name='面板数据', index=False)
        
        # 保存数据描述
        description = panel_df.describe()
        description.to_excel(writer, sheet_name='数据描述')
        
        # 保存专利数据统计
        patent_stats = panel_df[['patent_count', 'citation_count', 'invention_count', 'invention_citation']].describe()
        patent_stats.to_excel(writer, sheet_name='专利数据统计')
        
        # 保存控制变量统计
        control_stats = panel_df[['gdp', 'urban_rate', 'fixed_investment']].describe()
        control_stats.to_excel(writer, sheet_name='控制变量统计')
        
        # 保存分组统计
        group_stats = panel_df.groupby(['treatment', 'post']).agg({
            'patent_count': ['mean', 'std', 'count'],
            'citation_count': ['mean', 'std', 'count'],
            'gdp': ['mean', 'std'],
            'urban_rate': ['mean', 'std']
        }).round(4)
        group_stats.to_excel(writer, sheet_name='分组统计')
    
    # 8. 清理临时文件
    if os.path.exists('temp_panel_data.xlsx'):
        os.remove('temp_panel_data.xlsx')
    
    print(f"   - 数据已保存到: {output_file}")
    
    # 9. 显示最终统计
    print("\n8. 最终数据统计:")
    print(f"   - 总观测值: {len(panel_df):,}")
    print(f"   - 公司数: {panel_df['company'].nunique():,}")
    print(f"   - 年份数: {panel_df['year'].nunique()}")
    print(f"   - 总列数: {panel_df.shape[1]}")
    
    # 专利数据统计
    patent_summary = panel_df[['patent_count', 'citation_count', 'invention_count', 'invention_citation']].sum()
    print(f"\n9. 专利数据汇总:")
    print(patent_summary)
    
    return panel_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='创建增强的回归面板数据')
    parser.add_argument('--input_file', 
                       default='invest.xlsx',
                       help='投资数据文件路径')
    parser.add_argument('--sheet_name', 
                       default='有专利公司首次投资',
                       help='工作表名称')
    parser.add_argument('--patent_file', 
                       default='patent_analysis/company_patent_yearly.xlsx',
                       help='专利数据文件路径')
    parser.add_argument('--output_file', 
                       default='patent_analysis/enhanced_regression_panel_data.xlsx',
                       help='输出文件路径')
    
    args = parser.parse_args()
    
    # 创建增强的面板数据
    panel_df = create_enhanced_regression_data(
        input_file=args.input_file,
        sheet_name=args.sheet_name,
        patent_file=args.patent_file,
        output_file=args.output_file
    )
    
    print(f"\n=== 增强的回归面板数据创建完成 ===")
    print(f"输出文件: {args.output_file}")
    print(f"数据形状: {panel_df.shape}")
