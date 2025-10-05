#!/usr/bin/env python3
"""
创建用于回归的数据表
从invest中读取投资事件的公司、年份、省份、treatment，扩展年份的前三年和后三年成6行数据
"""

import pandas as pd
import numpy as np
import argparse
from datetime import datetime
import sys
sys.path.append('.')

from growth_regress import read_urban


PROVINCE = '省份'
STAGE = '投资阶段'
URBAN_RATE = '城镇化率'

def create_regression_data(input_file='invest.xlsx', 
                          sheet_name='有专利公司首次投资',
                          output_file='patent_analysis/regression_panel_data.xlsx'):
    """
    创建用于回归的面板数据
    
    参数:
    input_file: 投资数据文件路径
    sheet_name: 工作表名称
    output_file: 输出文件路径
    
    返回:
    panel_df: 面板数据DataFrame
    """
    print("=== 创建回归面板数据 ===")
    
    # 1. 读取投资数据
    print("1. 读取投资数据...")
    invest_df = pd.read_excel(input_file, sheet_name=sheet_name)
    print(f"   - 投资记录数: {len(invest_df):,}")
    print(f"   - 列名: {list(invest_df.columns)}")
    
    # 2. 数据预处理
    print("2. 数据预处理...")
    
    # 确保投资年份是整数
    invest_df['投资年份'] = pd.to_numeric(invest_df['投资年份'], errors='coerce')
    invest_df = invest_df.dropna(subset=['投资年份'])
    invest_df = invest_df[invest_df['投资年份'].astype(int) >= 2006]
    
    # 确保treatment是整数
    invest_df['treatment'] = pd.to_numeric(invest_df['treatment'], errors='coerce')
    invest_df = invest_df.dropna(subset=['treatment'])
    invest_df['treatment'] = invest_df['treatment'].astype(int)
    
    print(f"   - 有效投资记录数: {len(invest_df):,}")
    print(f"   - 投资年份范围: {invest_df['投资年份'].min()} - {invest_df['投资年份'].max()}")
    print(f"   - Treatment分布: {invest_df['treatment'].value_counts().to_dict()}")
    
    # 3. 创建面板数据
    print("3. 创建面板数据...")
    panel_data = []
    
    for idx, row in invest_df.iterrows():
        company = row['融资主体']
        investment_year = row['投资年份']
        treatment = row['treatment']
        province = row['省份']
        investment_stage = row['投资阶段']
        
        # 创建前3年和后3年的数据
        for year_offset in [-3, -2, -1, 1, 2, 3]:  
            year = investment_year + year_offset
            
            # 只保留合理年份范围的数据
            if 1990 <= year <= 2025:
                # 确定post变量（投资后为1，投资前为0）
                post = 1 if year_offset >= 0 else 0
                
                # 创建面板数据记录
                panel_record = {
                    'company': company,
                    'year': year,
                    # 'investment_year': investment_year,
                    'treatment': treatment,
                    'post': post,
                    'treatment_post': treatment * post,  # 交互项
                    PROVINCE: province,
                    STAGE: investment_stage,
                    'year_offset': year_offset,
                    'same_location':row['same_location']
                }
                
                panel_data.append(panel_record)
        
        # 显示进度
        if (idx + 1) % 1000 == 0:
            print(f"   - 已处理 {idx + 1:,} 个投资事件...")
    
    # 4. 创建面板数据框
    print("4. 创建面板数据框...")
    panel_df = pd.DataFrame(panel_data)
    print(f"   - 面板数据行数: {len(panel_df):,}")
    print(f"   - 面板数据列数: {len(panel_df.columns)}")
    
    # 5. 数据统计
    print("5. 数据统计...")
    print(f"   - 公司数量: {panel_df['company'].nunique():,}")
    print(f"   - 年份范围: {panel_df['year'].min()} - {panel_df['year'].max()}")
   
    # 按treatment和post分组统计
    group_stats = panel_df.groupby(['treatment', 'post']).agg('count').reset_index()
    print(f"\n6. 分组统计:")
    print(group_stats)
    
    # 按省份统计
    province_stats = panel_df.groupby(PROVINCE).size().sort_values(ascending=False).reset_index()
    print(f"\n7. 省份统计 (前10):")
    print(province_stats.head(10))
    
    # 按投资阶段统计
    stage_stats = panel_df.groupby(STAGE).size().sort_values(ascending=False).reset_index()
    print(f"\n8. 投资阶段统计:")
    print(stage_stats)
    
    year_stats = panel_df.groupby('year').size().reset_index()
    print(f"\n9. 年份统计:")
    print(year_stats)

    # 6. 保存数据
    print("9. 保存数据...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 保存面板数据
        panel_df.to_excel(writer, sheet_name='面板数据', index=False)
        
        # 保存统计信息
        group_stats.to_excel(writer, sheet_name='分组统计', index=False)
        province_stats.to_excel(writer, sheet_name='省份统计', index=False)
        stage_stats.to_excel(writer, sheet_name='投资阶段统计', index=False)
        year_stats.to_excel(writer, sheet_name='年份统计', index=False)
    
    print(f"   - 数据已保存到: {output_file}")
    
    # 7. 显示示例数据
    print("\n10. 示例数据:")
    print("面板数据前10行:")
    print(panel_df.head(5))
    
    print(f"\n=== 面板数据创建完成 ===")
    print(f"总记录数: {len(panel_df):,}")
    print(f"公司数: {panel_df['company'].nunique():,}")
    print(f"年份数: {panel_df['year'].nunique()}")
    print(f"输出文件: {output_file}")
    
    return panel_df

def read_panel_data()->pd.DataFrame:
    file = 'patent_analysis/regression_panel_data.xlsx'
    sheet_name = '面板数据'
    return pd.read_excel(file, sheet_name=sheet_name)

def write_panel_data(panel_df, output_file,sheet_name = '面板数据'):
    
    with pd.ExcelWriter(output_file, engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        panel_df.to_excel(writer, sheet_name=sheet_name, index=False)

def add_patent(df)->pd.DataFrame:
    patent_file = 'patent_analysis/company_patent_yearly.xlsx'
    patent_dict = pd.read_excel(patent_file, sheet_name=None)
    sheet_names = ['专利数量', '被引证次数', '发明数量', '发明被引证次数']
    if sheet_names[0] in patent_dict and sheet_names[1] in patent_dict and sheet_names[2] in patent_dict and sheet_names[3] in patent_dict:
        patent_df = patent_dict[sheet_names[0]]
        citation_df = patent_dict[sheet_names[1]]
        invention_df = patent_dict[sheet_names[2]]
        invention_citation_df = patent_dict[sheet_names[3]]
        col_name = 'Unnamed: 0'
        patent_df.set_index(col_name, inplace=True)
        citation_df.set_index(col_name, inplace=True)
        invention_df.set_index(col_name, inplace=True)
        invention_citation_df.set_index(col_name, inplace=True)
    else:
        print(f"专利数据文件中没有找全{sheet_names}工作表")
        return

    def _add_row_data(df:pd.Series, patent_df, citation_df, invention_df, invention_citation_df):
        company = df['company']
        year = 'y' + str(df['year'])
        patent_count = patent_df.loc[company, year]
        citation_count = citation_df.loc[company, year]
        invention_count = invention_df.loc[company, year]
        invention_citation_count = invention_citation_df.loc[company, year]
        df['patent_count'] = patent_count
        df['citation_count'] = citation_count
        df['invention_count'] = invention_count
        df['invention_citation'] = invention_citation_count
        return df

    df = df.apply(_add_row_data, axis=1, args=(patent_df, citation_df, invention_df, invention_citation_df))
    return df       

def add_gdp(df):
    print("=== 添加省份GDP数据 ===")
    
    # 2. 读取GDP数据
    print("2. 读取GDP数据...")
    gdp_df = pd.read_excel('gdp.xlsx',index_col=[0,1])
    print(f"   - GDP数据行数: {len(gdp_df):,}")
    
    def _add_row_data(row:pd.Series, gdp_df):
        province ,year = row[PROVINCE],row['year']
        try:
            row['GDP'] = gdp_df.loc[(year, province)]['地区生产总值/亿元']
            return row
        except Exception as e:
            print(f"  错误: 处理gdp{province}{year}数据时发生异常: {e}")

    df = df.apply(_add_row_data, axis=1, args=(gdp_df,))
    return df
    

def add_urban_col(df):
    from growth_regress import read_urban
    urban_df = read_urban() 

    def _add_row_data(row:pd.Series, urban_df):
        province ,year = row[PROVINCE],row['year']
        try:
            if year == 2024:
                year = 2023
            row[URBAN_RATE] = urban_df.loc[province, str(year)]
            return row
        except Exception as e:
            print(f"  错误: 处理{province}{year}数据时发生异常: {e}")

    df = df.apply(_add_row_data, axis=1, args=(urban_df,))
    
    return df

def add_fixed_invest_col(df):
    from growth_regress import read_fixed_invest
    investment_df, investment_col = read_fixed_invest()
    def _add_row_data(row:pd.Series, investment_df, investment_col):
        province ,year= row[PROVINCE],row['year']
        if year == 2024:
            year = 2023
        row['固定资产投资'] = investment_df.loc[year,province][investment_col]
        return row

    df = df.apply(_add_row_data, axis=1, args=(investment_df, investment_col))
    return df

def add_employment_col(df):
    # 第二产业从业人口占比
    employment_df = pd.read_excel('就业人口.xlsx',index_col=[1,2]) #年份，省份

    def _add_row_data(row:pd.Series, employment_df):
        province ,year= row[PROVINCE],row['year']
        if year == 2024:
            year = 2023
        row['二产就业比例'] = employment_df.loc[year,province]['第二产业就业人员比例(%)']
        return row

    df = df.apply(_add_row_data, axis=1, args=(employment_df,))
    
    return df

def add_stage(df):
    invest_df = pd.read_excel('invest.xlsx')
    def _add_stage(row, invest_df):
        company = row['company']
        filtered_invest_df = invest_df[invest_df['融资主体'] == company]
        if len(filtered_invest_df) == 0:
            print('error: not found investment')
        stage = filtered_invest_df.iloc[0]['投资阶段']
        row['stage'] = stage
        return row

    df = df.apply(_add_stage, axis = 1, args=(invest_df,))
    return df

def add_region(df):
    EAST = ['北京','天津','河北','上海','江苏','浙江','福建','山东','广东','海南']
    MIDDLE = ['山西','安徽','江西','河南','湖北','湖南']
    WEST = ['内蒙古','广西','重庆','四川','贵州','云南','西藏','陕西','甘肃','青海','宁夏','新疆']
    NORTHEAST = ['辽宁','吉林','黑龙江']
    def _add_region(row):
        province = row['原省份']
        if province.endswith('省') or province.endswith('市'):
            province = province[:-1]
        if province in EAST:
            return '东部'
        elif province in MIDDLE:
            return '中部'
        elif province in WEST:
            return '西部'
        elif province in NORTHEAST:
            return '东北'
        return ''
    df['region'] = df.apply(_add_region, axis=1)
    return df

def _generate_dummy_variables(panel_df):
    REGION = 'region'
    print("生成虚拟变量...")
    # province_cols = panel_df[PROVINCE]
    # 使用pd.get_dummies创建省份虚拟变量
    # panel_dummies = pd.get_dummies(panel_df, columns=[PROVINCE,STAGE,REGION], prefix=[PROVINCE,STAGE,REGION], drop_first=True, dtype=int)
    # panel_dummies['原省份'] = panel_df[PROVINCE]
    panel_dummies = pd.get_dummies(panel_df, columns=[REGION], prefix=[REGION], drop_first=True, dtype=int)
    
    print("   - 创建虚拟变量完成 ")
    return panel_dummies

def main(args):
    # 创建面板数据
    # panel_df = create_regression_data(
    #     input_file=args.input_file,
    #     sheet_name=args.sheet_name,
    #     output_file=args.output_file
    # )
    panel_df = read_panel_data()
    # panel_df = add_gdp(panel_df)
    # panel_df = add_patent(panel_df)
    # panel_df = add_urban_col(panel_df)
    # panel_df = add_fixed_invest_col(panel_df)
    # panel_df = add_employment_col(panel_df)
    # panel_df = add_stage(panel_df)
    panel_df = add_region(panel_df)
    print(panel_df.head(5))
    print(panel_df.columns)
    panel_df = _generate_dummy_variables(panel_df)
    
    write_panel_data(panel_df, args.output_file,sheet_name = '面板数据1')
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='创建回归面板数据')
    parser.add_argument('--input_file', 
                       default='invest.xlsx',
                       help='投资数据文件路径')
    parser.add_argument('--sheet_name', 
                    #    default='有专利公司首次投资',
                       default='location',
                       help='工作表名称')
    parser.add_argument('--output_file', 
                       default='patent_analysis/regression_panel_data.xlsx',
                    #    default='patent_analysis/regression_data_location.xlsx',
                       help='输出文件路径')
    parser.add_argument('--analyze', 
                       action='store_true',
                       help='是否进行详细分析')
    
    args = parser.parse_args()
    main(args)
  
