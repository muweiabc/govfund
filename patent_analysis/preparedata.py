import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def _read_input_data(patent_data_file=None, data_type='patent_count'):
    """
    读取输入数据：首次投资数据和专利年度数据
    
    参数:
    patent_data_file: 专利数据文件路径，如果为None则使用默认文件
    data_type: 数据类型，'patent_count'表示专利数量，'citation_count'表示被引证次数
    
    返回:
    tuple: (first_investments_df, patent_df, sheet_name)
    """
    print("=== 读取输入数据 ===")
    print(f"数据类型: {data_type}")
    
    # 1. 读取首次投资数据
    print("1. 读取首次投资数据...")
    first_investments_df = pd.read_excel('invest.xlsx', sheet_name='有专利公司首次投资')
    
    print(f"   - 首次投资记录数: {len(first_investments_df):,}")
    
    # 2. 读取专利年度数据
    print("2. 读取专利年度数据...")
    
    # 根据数据类型选择默认文件
    if patent_data_file is None:
        if data_type == 'patent_count':
            patent_data_file = 'patent_analysis/company_patent_yearly.xlsx'
            sheet_name = '有专利公司'
        elif data_type == 'citation_count':
            patent_data_file = 'patent_analysis/company_patent_citations_yearly.xlsx'
            sheet_name = '被引证次数'
        else:
            raise ValueError("data_type必须是'patent_count'或'citation_count'")
    else:
        # 如果指定了文件，尝试自动检测sheet名称
        if data_type == 'patent_count':
            sheet_name = '有专利公司'
        elif data_type == 'citation_count':
            sheet_name = '被引证次数'
        else:
            sheet_name = None

    try:
        patent_df = pd.read_excel('patent_analysis/' + patent_data_file, sheet_name=sheet_name)
    except:
        # 如果指定的sheet不存在，尝试第一个sheet
        patent_df = pd.read_excel(patent_data_file, sheet_name=0)
        print(f"   - 使用默认sheet: {patent_df.columns[0]}")
    
    print(f"   - 专利数据文件: {patent_data_file}")
    print(f"   - 有专利公司数: {len(patent_df):,}")
    
    return first_investments_df, patent_df, sheet_name

def _extract_timeline_data(first_investments_df, patent_df, data_type):
    """
    提取投资前后3年的专利时间序列数据
    
    参数:
    first_investments_df: 首次投资数据框
    patent_df: 专利数据框
    data_type: 数据类型，'patent_count'表示专利数量，'citation_count'表示被引证次数
    
    返回:
    list: 时间序列数据记录列表
    """
    print("4. 提取投资前后3年专利数据...")
    
    # 获取年份列
    year_columns = list(range(1992, 2026))
    print(f"   - 专利数据年份范围: {min(year_columns)} - {max(year_columns)}")
    
    # 创建结果数据结构
    timeline_data = []
    
    for idx, row in first_investments_df.iterrows():
        company_name = row['融资主体']
        investment_year = row['投资年份']
        treatment = row['treatment']
        
        # 在专利数据中查找该公司
        # 尝试不同的列名来匹配公司名称
        company_patent_data = None
        company_name_col = None
        
        # 查找公司名称列
        for col in patent_df.columns:
            if '公司' in col or '名称' in col or '申请人' in col or col == 'Unnamed: 0':
                if company_name in patent_df[col].values:
                    company_name_col = col
                    company_patent_data = patent_df[patent_df[col] == company_name]
                    break
        
        if company_patent_data is None:
            # 如果没找到，尝试直接匹配索引
            if company_name in patent_df.index:
                company_patent_data = patent_df.loc[[company_name]]
                company_name_col = 'index'
        
        if len(company_patent_data) > 0:
            # 计算前3年和后3年的年份范围
            pre_years = [investment_year - 3, investment_year - 2, investment_year - 1]
            post_years = [investment_year + 1, investment_year + 2, investment_year + 3]
            
            # 提取专利数据
            patent_counts = {}
            
            # 前3年专利数
            for year in pre_years:
                if year in year_columns:
                    year_str = 'y' + str(year)
                    if year_str in patent_df.columns:
                        patent_count = company_patent_data[year_str].iloc[0]
                        patent_counts[f'前{investment_year - year}年'] = int(patent_count) if pd.notna(patent_count) else 0
                    else:
                        patent_counts[f'前{investment_year - year}年'] = 0
                else:
                    patent_counts[f'前{investment_year - year}年'] = 0

            # 投资当年专利数
            if investment_year in year_columns:
                year_str = 'y' + str(investment_year)
                if year_str in patent_df.columns:
                    if company_name_col == 'index':
                        patent_count = company_patent_data[year_str].iloc[0]
                    else:
                        patent_count = company_patent_data[year_str].iloc[0]
                    patent_counts['投资当年'] = int(patent_count) if pd.notna(patent_count) else 0
                else:
                    patent_counts['投资当年'] = 0
            else:
                patent_counts['投资当年'] = 0
            
            # 后3年专利数
            for year in post_years:
                if year in year_columns:
                    year_str = 'y' + str(year)
                    if year_str in patent_df.columns:
                        if company_name_col == 'index':
                            patent_count = company_patent_data[year_str].iloc[0]
                        else:
                            patent_count = company_patent_data[year_str].iloc[0]
                        patent_counts[f'后{year - investment_year}年'] = int(patent_count) if pd.notna(patent_count) else 0
                    else:
                        patent_counts[f'后{year - investment_year}年'] = 0
                else:
                    patent_counts[f'后{year - investment_year}年'] = 0
            
            # 计算总计
            pre_total = sum([patent_counts[f'前{i}年'] for i in range(1, 4)])
            post_total = sum([patent_counts[f'后{i}年'] for i in range(1, 4)])
            
            # 根据数据类型调整列名
            if data_type == 'citation_count':
                # 被引证次数数据
                record = {
                    '公司名称': company_name,
                    '投资年份': investment_year,
                    '投资时间': row['投资时间'],
                    'treatment': treatment,
                    '前3年被引证总数': pre_total,
                    '投资当年被引证数': patent_counts['投资当年'],
                    '后3年被引证总数': post_total,
                    '前3年被引证数_前1年': patent_counts['前1年'],
                    '前3年被引证数_前2年': patent_counts['前2年'],
                    '前3年被引证数_前3年': patent_counts['前3年'],
                    '后3年被引证数_后1年': patent_counts['后1年'],
                    '后3年被引证数_后2年': patent_counts['后2年'],
                    '后3年被引证数_后3年': patent_counts['后3年'],
                    '被引证增长率': ((post_total - pre_total) / max(pre_total, 1)) * 100 if pre_total > 0 else 0,
                    '投资阶段': row['投资阶段'],
                    '省份': row['省份']
                }
            else:
                # 专利数量数据
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
                    '专利增长率': ((post_total - pre_total) / max(pre_total, 1)) * 100 if pre_total > 0 else 0,
                    '投资阶段': row['投资阶段'],
                    '省份': row['省份']
                }
            
            if (patent_counts['前1年'] > 0) or (patent_counts['后1年'] > 0) or (patent_counts['前2年'] > 0) or (patent_counts['后2年'] > 0) or (patent_counts['前3年'] > 0) or (patent_counts['后3年'] > 0):
                timeline_data.append(record)
        
        # 显示进度
        if (idx + 1) % 1000 == 0:
            print(f"   - 已处理 {idx + 1:,} 家公司...")
    
    return pd.DataFrame(timeline_data)

def _save_results(timeline_df, data_type):
    """
    保存分析结果到Excel文件
    
    参数:
    timeline_df: 时间序列数据框
    data_type: 数据类型，'patent_count'表示专利数量，'citation_count'表示被引证次数
    
    返回:
    str: 保存的Excel文件路径
    """
    print("7. 保存数据...")
    
    # 根据数据类型生成不同的文件名
    path = 'patent_analysis/'
    if data_type == 'citation_count':
        excel_filename = path +'regress_data_citations.xlsx'
        sheet_name_summary = '被引证次数数据统计'
        sheet_name_yearly = '被引证次数按年份统计'
    else:
        excel_filename = path + 'regress_data_patents.xlsx'
        sheet_name_summary = '专利数量数据统计'
        sheet_name_yearly = '专利数量按年份统计'
    
    # 保存为Excel文件
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        timeline_df.to_excel(writer, sheet_name='回归数据', index=False)
        
        # 创建汇总统计sheet
        summary_stats = timeline_df.describe()
        summary_stats.to_excel(writer, sheet_name=sheet_name_summary)
        
        # 按年份统计
        if data_type == 'citation_count':
            yearly_stats = timeline_df.groupby('投资年份').agg({
                '前3年被引证总数': 'mean',
                '后3年被引证总数': 'mean',
                '被引证增长率': 'mean',
                'treatment': 'count'
            }).round(2)
        else:
            yearly_stats = timeline_df.groupby('投资年份').agg({
                '前3年专利总数': 'mean',
                '后3年专利总数': 'mean',
                '专利增长率': 'mean',
                'treatment': 'count'
            }).round(2)
        yearly_stats.to_excel(writer, sheet_name=sheet_name_yearly)

        timeline_df.to_excel(writer, sheet_name='回归数据', index=False)
            
            # 创建汇总统计sheet
        summary_stats = timeline_df.describe()
        summary_stats.to_excel(writer, sheet_name='数据统计')
        
        # 动态识别列名
        total_columns = [col for col in timeline_df.columns if '前3年' in col and '总数' in col]
        growth_columns = [col for col in timeline_df.columns if '增长率' in col]
        
        # 按年份统计
        agg_dict = {'treatment': 'count'}
        for col in total_columns:
            agg_dict[col] = 'mean'
        for col in growth_columns:
            agg_dict[col] = 'mean'
        
        yearly_stats = timeline_df.groupby('投资年份').agg(agg_dict).round(2)
        yearly_stats.to_excel(writer, sheet_name='按年份统计')
        
        # 按省份统计
        agg_dict_province = {'treatment': 'count'}
        for col in total_columns:
            agg_dict_province[col] = ['mean', 'count']
        for col in growth_columns:
            agg_dict_province[col] = 'mean'
        
        province_stats = timeline_df.groupby('省份').agg(agg_dict_province).round(2)
        province_stats.to_excel(writer, sheet_name='按省份统计')
 

    print(f"   - Excel文件已保存: {excel_filename}")
    return excel_filename

def extract_regress_data(patent_data_file=None, data_type='patent_count'):
    """
    从invest读取公司首次获投资的时间，
    从专利数据中获取该公司在获得投资前3年和后3年的专利数或被引证次数，
    保存为合适的数据结构
    
    参数:
    patent_data_file: 专利数据文件路径，如果为None则使用默认文件
    data_type: 数据类型，'patent_count'表示专利数量，'citation_count'表示被引证次数
    """
    try:
        print("=== 提取投资前后专利时间序列数据 ===")
        
        # 1. 读取输入数据
        first_investments_df, patent_df, sheet_name = _read_input_data(patent_data_file, data_type)
        
        # 2. 处理投资时间，转换为年份
        print("2. 处理投资时间...")
        first_investments_df['投资年份'] = pd.to_datetime(first_investments_df['投资时间']).dt.year
        print(f"   - 投资年份范围: {first_investments_df['投资年份'].min()} - {first_investments_df['投资年份'].max()}")
        
        # 3. 提取时间序列数据
        timeline_data = _extract_timeline_data(first_investments_df, patent_df, data_type)
        data_with_gdp = _add_gdp(timeline_data, data_type)

        # 4. 创建数据框
        print("4. 创建数据框...")
        timeline_df = pd.DataFrame(timeline_data)
        print(f"   - 成功提取数据: {len(timeline_df):,} 家公司")
        
        # 5. 数据统计
        print("5. 数据统计...")
        print(f"   - 有投资记录的公司: {len(timeline_df):,}")
        
        # 按treatment分组统计
        if 'treatment' in timeline_df.columns:
            if data_type == 'citation_count':
                treatment_stats = timeline_df.groupby('treatment').agg({
                    '前3年被引证总数': ['mean', 'median', 'sum'],
                    '后3年被引证总数': ['mean', 'median', 'sum'],
                    '被引证增长率': ['mean', 'median']
                }).round(2)
            else:
                treatment_stats = timeline_df.groupby('treatment').agg({
                    '前3年专利总数': ['mean', 'median', 'sum'],
                    '后3年专利总数': ['mean', 'median', 'sum'],
                    '专利增长率': ['mean', 'median']
                }).round(2)
            
            print(f"\n6. Treatment分组统计:")
            print(treatment_stats)
        
        # 6. 保存数据
        excel_filename = _save_results(timeline_df, data_type)
     
        return {
            'timeline_df': timeline_df,
            'excel_file': excel_filename,
            'total_companies': len(timeline_df),
            'year_range': f"{timeline_df['投资年份'].astype(int).min()} - {timeline_df['投资年份'].astype(int).max()}",
            'data_type': data_type
        }
        
    except FileNotFoundError as e:
        print(f"文件未找到错误: {e}")
        return None
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_regress_data_patents():
    """
    提取专利数量数据的便捷函数
    """
    return extract_regress_data(patent_data_file='company_patent_yearly.xlsx', data_type='patent_count')

def extract_regress_data_citations():
    """
    提取被引证次数数据的便捷函数
    """
    return extract_regress_data(patent_data_file='company_citations_yearly.xlsx', data_type='citation_count')

def _add_gdp(timeline_df, data_type):
    """
    添加GDP数据
    """
    print("=== 添加省份GDP数据 ===")
    
    # 2. 读取GDP数据
    print("2. 读取GDP数据...")
    gdp_df = pd.read_excel('gdp.xlsx')
    print(f"   - GDP数据行数: {len(gdp_df):,}")
    print(f"   - GDP数据年份范围: {gdp_df['年份'].min()} - {gdp_df['年份'].max()}")
    
    # 3. 创建省份年份到GDP的映射
    print("3. 创建省份年份到GDP的映射...")
    gdp_map = {}
    
    for idx, row in gdp_df.iterrows():
        year = row['年份']
        province = row['省级']
        gdp_value = row['地区生产总值/亿元']
        
        if pd.notna(gdp_value) and gdp_value > 0:
            gdp_map[(province, year)] = gdp_value
    
    print(f"   - 成功创建GDP映射: {len(gdp_map):,} 个省份-年份组合")

    # 4. 为每个公司添加投资前后年份的GDP数据
    print("4. 为每个公司添加投资前后年份的GDP数据...")
    
    # 创建新的GDP列
    timeline_df['前3年GDP_前1年'] = 0
    timeline_df['前3年GDP_前2年'] = 0
    timeline_df['前3年GDP_前3年'] = 0
    timeline_df['投资当年GDP'] = 0
    timeline_df['后3年GDP_后1年'] = 0
    timeline_df['后3年GDP_后2年'] = 0
    timeline_df['后3年GDP_后3年'] = 0
    
    # 添加ln(GDP+1)列
    timeline_df['ln_前3年GDP_前1年'] = 0
    timeline_df['ln_前3年GDP_前2年'] = 0
    timeline_df['ln_前3年GDP_前3年'] = 0
    timeline_df['ln_投资当年GDP'] = 0
    timeline_df['ln_后3年GDP_后1年'] = 0
    timeline_df['ln_后3年GDP_后2年'] = 0
    timeline_df['ln_后3年GDP_后3年'] = 0
    
    # 统计GDP数据匹配情况
    matched_count = 0
    total_attempts = 0
    
    for idx, row in timeline_df.iterrows():
        
        investment_year = row['投资年份']
        province = row['省份']
        
        if pd.isna(province):
            continue
        
        total_attempts += 1
        
        # 前3年GDP
        for year_offset in range(1, 4):
            year = investment_year - year_offset
            gdp_key = (province, year)
            
            if gdp_key in gdp_map:
                gdp_value = gdp_map[gdp_key]
                timeline_df.at[idx, f'前3年GDP_前{year_offset}年'] = gdp_value
                timeline_df.at[idx, f'ln_前3年GDP_前{year_offset}年'] = np.log(gdp_value + 1)
                matched_count += 1
        
        # 投资当年GDP
        gdp_key = (province, investment_year)
        if gdp_key in gdp_map:
            gdp_value = gdp_map[gdp_key]
            timeline_df.at[idx, '投资当年GDP'] = gdp_value
            timeline_df.at[idx, 'ln_投资当年GDP'] = np.log(gdp_value + 1)
            matched_count += 1
        
        # 后3年GDP
        for year_offset in range(1, 4):
            year = investment_year + year_offset
            gdp_key = (province, year)
            
            if gdp_key in gdp_map:
                gdp_value = gdp_map[gdp_key]
                timeline_df.at[idx, f'后3年GDP_后{year_offset}年'] = gdp_value
                timeline_df.at[idx, f'ln_后3年GDP_后{year_offset}年'] = np.log(gdp_value + 1)
                matched_count += 1
        
        # 显示进度
        if (idx + 1) % 1000 == 0:
            print(f"   - 已处理 {idx + 1:,} 家公司...")
    
    # 5. 统计GDP数据匹配情况
    print(f"\n5. GDP数据匹配统计:")
    print(f"   - 总尝试次数: {total_attempts:,}")
    print(f"   - 成功匹配次数: {matched_count:,}")
    print(f"   - 匹配率: {matched_count / total_attempts * 100:.2f}%")

    if data_type == 'citation_count':
        output_filename = 'regress_data_citations_with_gdp.xlsx'
    else:
        outputtput_filename = 'regress_data_patents_with_gdp.xlsx'


    return 

if __name__ == "__main__":
    print("=== 专利数量数据分析 ===")
    # 提取投资前后专利数量时间序列数据
    # result_patents = extract_regress_data_patents()
    
    print("\n" + "="*60)
    print("=== 被引证次数数据分析 ===")
    # 提取投资前后被引证次数时间序列数据
    result_citations = extract_regress_data_patents()
    
    # 显示结果摘要
    # if result_patents:
    #     print(f"\n专利数量分析结果:")
    #     print(f"  - 文件: {result_patents['excel_file']}")
    #     print(f"  - 公司数: {result_patents['total_companies']}")
    #     print(f"  - 年份范围: {result_patents['year_range']}")
    
    if result_citations:
        print(f"\n被引证次数分析结果:")
        print(f"  - 文件: {result_citations['excel_file']}")
        print(f"  - 公司数: {result_citations['total_companies']}")
        print(f"  - 年份范围: {result_citations['year_range']}")
    
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
