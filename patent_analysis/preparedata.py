import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def extract_regress_data():
    """
    从invest读取公司首次获投资的时间，
    从company_patent_yearly中的"有专利公司"sheet中获取该公司在获得投资前3年和后3年的专利数，
    保存为合适的数据结构
    """
    try:
        print("=== 提取投资前后专利时间序列数据 ===")
        
        # 1. 读取首次投资数据
        print("1. 读取首次投资数据...")
        first_investments_df = pd.read_excel('invest.xlsx', sheet_name='有专利公司首次投资')
        print(f"   - 首次投资记录数: {len(first_investments_df):,}")
        
        # 2. 读取专利年度数据
        print("2. 读取专利年度数据...")
        patent_df = pd.read_excel('company_patent_yearly.xlsx', sheet_name='有专利公司')
        print(f"   - 有专利公司数: {len(patent_df):,}")
        
        # 3. 处理投资时间，转换为年份
        print("3. 处理投资时间...")
        first_investments_df['投资年份'] = pd.to_datetime(first_investments_df['投资时间']).dt.year
        print(f"   - 投资年份范围: {first_investments_df['投资年份'].min()} - {first_investments_df['投资年份'].max()}")
        
        # 4. 创建专利时间序列数据结构
        print("4. 创建专利时间序列数据结构...")
        
        # 获取年份列（排除非年份列）
        year_columns = [col for col in patent_df.columns if str(col).isdigit()]
        year_columns = sorted([int(col) for col in year_columns])
        print(f"   - 专利数据年份范围: {min(year_columns)} - {max(year_columns)}")
        
        # 创建结果数据结构
        timeline_data = []
        
        # 5. 为每个公司提取投资前后3年的专利数据
        print("5. 提取投资前后3年专利数据...")
        
        for idx, row in first_investments_df.iterrows():
            company_name = row['融资主体']
            investment_year = row['投资年份']
            treatment = row['treatment']
            
            # 在专利数据中查找该公司
            company_patent_data = patent_df[patent_df['Unnamed: 0'] == company_name]
            
            if len(company_patent_data) > 0:
                # 计算前3年和后3年的年份范围
                pre_years = [investment_year - 3, investment_year - 2, investment_year - 1]
                post_years = [investment_year + 1, investment_year + 2, investment_year + 3]
                
                # 提取专利数据
                patent_counts = {}
                
                # 前3年专利数
                for year in pre_years:
                    if year in year_columns:
                        year_str = str(year)
                        if year_str in patent_df.columns:
                            patent_count = company_patent_data[year_str].iloc[0]
                            patent_counts[f'前{investment_year - year}年'] = int(patent_count) if pd.notna(patent_count) else 0
                        else:
                            patent_counts[f'前{investment_year - year}年'] = 0
                    else:
                        patent_counts[f'前{investment_year - year}年'] = 0
                
                # 投资当年专利数
                if investment_year in year_columns:
                    year_str = str(investment_year)
                    if year_str in patent_df.columns:
                        patent_count = company_patent_data[year_str].iloc[0]
                        patent_counts['投资当年'] = int(patent_count) if pd.notna(patent_count) else 0
                    else:
                        patent_counts['投资当年'] = 0
                else:
                    patent_counts['投资当年'] = 0
                
                # 后3年专利数
                for year in post_years:
                    if year in year_columns:
                        year_str = str(year)
                        if year_str in patent_df.columns:
                            patent_count = company_patent_data[year_str].iloc[0]
                            patent_counts[f'后{year - investment_year}年'] = int(patent_count) if pd.notna(patent_count) else 0
                        else:
                            patent_counts[f'后{year - investment_year}年'] = 0
                    else:
                        patent_counts[f'后{year - investment_year}年'] = 0
                
                # 计算总计
                pre_total = sum([patent_counts[f'前{i}年'] for i in range(1, 4)])
                post_total = sum([patent_counts[f'后{i}年'] for i in range(1, 4)])
                
                
                # 创建记录
                record = {
                    '公司名称': company_name,
                    '投资年份': investment_year,
                    '投资时间': row['投资时间'],
                    'treatment': treatment,
                    '前3年专利总数': pre_total,
                    '投资当年专利数': patent_counts['投资当年'],
                    '后3年专利总数': post_total,
                    '前3年专利数_前1年': patent_counts['前1年'],
                    '前3年专利数_前2年': patent_counts['前2年'],
                    '前3年专利数_前3年': patent_counts['前3年'],
                    '后3年专利数_后1年': patent_counts['后1年'],
                    '后3年专利数_后2年': patent_counts['后2年'],
                    '后3年专利数_后3年': patent_counts['后3年'],
                    '专利增长率': ((post_total - pre_total) / max(pre_total, 1)) * 100 if pre_total > 0 else 0
                }
                
                if (patent_counts['前1年'] > 0) or (patent_counts['后1年'] > 0) or (patent_counts['前2年'] > 0) or (patent_counts['后2年'] > 0) or (patent_counts['前3年'] > 0) or (patent_counts['后3年'] > 0):
                    timeline_data.append(record)
            
            # 显示进度
            if (idx + 1) % 1000 == 0:
                print(f"   - 已处理 {idx + 1:,} 家公司...")
        
        # 6. 创建数据框
        print("6. 创建数据框...")
        timeline_df = pd.DataFrame(timeline_data)
        print(f"   - 成功提取数据: {len(timeline_df):,} 家公司")
        
        # 7. 数据统计
        print("7. 数据统计...")
        print(f"   - 有投资记录的公司: {len(timeline_df):,}")
        print(f"   - 投资年份范围: {timeline_df['投资年份'].min()} - {timeline_df['投资年份'].max()}")
        
        # 按treatment分组统计
        if 'treatment' in timeline_df.columns:
            treatment_stats = timeline_df.groupby('treatment').agg({
                '前3年专利总数': ['mean', 'median', 'sum'],
                '后3年专利总数': ['mean', 'median', 'sum'],
                '专利增长率': ['mean', 'median']
            }).round(2)
            
            print(f"\n8. Treatment分组统计:")
            print(treatment_stats)
        
        # 8. 保存数据
        print("9. 保存数据...")
        
        # 保存为Excel文件
        excel_filename = 'regress_data.xlsx'
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            timeline_df.to_excel(writer, sheet_name='回归数据', index=False)
            
            # 创建汇总统计sheet
            summary_stats = timeline_df.describe()
            summary_stats.to_excel(writer, sheet_name='数据统计')
            
            # 按年份统计
            yearly_stats = timeline_df.groupby('投资年份').agg({
                '前3年专利总数': 'mean',
                '后3年专利总数': 'mean',
                '专利增长率': 'mean',
                'treatment': 'count'
            }).round(2)
            yearly_stats.to_excel(writer, sheet_name='按年份统计')
        
        print(f"   - Excel文件已保存: {excel_filename}")
     
        return {
            'timeline_df': timeline_df,
            'excel_file': excel_filename,
            'total_companies': len(timeline_df),
            'year_range': f"{timeline_df['投资年份'].min()} - {timeline_df['投资年份'].max()}"
        }
        
    except FileNotFoundError as e:
        print(f"文件未找到错误: {e}")
        return None
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 提取投资前后专利时间序列数据
    result = extract_regress_data()
    
    # 执行DID回归分析
    # result = perform_did_regression()
    
    # 执行带GDP控制变量的DID回归分析
    # result = perform_did_regression_with_gdp()
    
    # if result:
        # print(f"\n=== 带GDP控制变量的DID回归分析完成 ===")
        # print(f"DID效应系数: {result['did_effect']:.4f}")
        # print(f"t值: {result['did_t_value']:.4f}")
        # print(f"p值: {result['did_p_value']:.4f}")
        # print(f"GDP控制变量系数: {result['gdp_effect']:.4f}")
        # print(f"面板数据文件: {result['panel_file']}")
        
        # if result['did_p_value'] < 0.05:
        #     print("✅ DID效应在5%水平上显著")
        # elif result['did_p_value'] < 0.1:
        #     print("⚠️ DID效应在10%水平上显著")
        # else:
        #     print("❌ DID效应不显著")
