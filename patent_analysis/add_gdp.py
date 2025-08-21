import pandas as pd
import re
import numpy as np

def extract_province_from_region():
    """
    读取regress_data，找到每个公司在invest的地区列里的省份名，加到该行里
    """
    try:
        print("=== 提取公司所在省份信息 ===")
        
        # 1. 读取patent_investment_timeline数据
        print("1. 读取regress_data数据...")
        timeline_df = pd.read_excel('regress_data.xlsx', sheet_name='回归数据')
        print(f"   - 数据行数: {len(timeline_df):,}")
        
        # 2. 读取invest_with_treatment数据
        print("2. 读取invest数据...")
        invest_df = pd.read_excel('invest.xlsx', sheet_name='有专利公司首次投资')
        print(f"   - 投资数据行数: {len(invest_df):,}")
        
        # 3. 创建公司名称到省份的映射
        print("3. 创建公司名称到省份的映射...")
        company_province_map = {}
        
        for idx, row in invest_df.iterrows():
            company_name = row['融资主体']
            region = row['地区']
            
            # 从地区列提取省份名
            province = extract_province(region)
            if province:
                company_province_map[company_name] = province
        
        print(f"   - 成功提取省份信息的公司数: {len(company_province_map):,}")
        
        # 4. 将省份信息添加到timeline数据中
        print("4. 将省份信息添加到regress_data数据中...")
        timeline_df['省份'] = timeline_df['公司名称'].map(company_province_map)
        
        # 统计省份分布
        province_counts = timeline_df['省份'].value_counts()
        print(f"   - 省份分布:")
        for province, count in province_counts.head(10).items():
            print(f"     {province}: {count:,}")
        
        # 5. 检查缺失值
        missing_province = timeline_df['省份'].isna().sum()
        print(f"\n5. 缺失值统计:")
        print(f"   - 有省份信息的公司: {len(timeline_df) - missing_province:,}")
        print(f"   - 缺失省份信息的公司: {missing_province:,}")
        
        if missing_province > 0:
            print(f"   - 缺失省份信息的公司示例:")
            missing_companies = timeline_df[timeline_df['省份'].isna()]['公司名称'].head(5).tolist()
            for company in missing_companies:
                print(f"     * {company}")
        
        # 6. 保存更新后的数据
        print("\n6. 保存更新后的数据...")
        output_filename = 'regress_data_with_province.xlsx'
        
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            timeline_df.to_excel(writer, sheet_name='投资前后专利数据', index=False)
            
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
            
            # 按省份统计
            province_stats = timeline_df.groupby('省份').agg({
                '前3年专利总数': ['mean', 'count'],
                '后3年专利总数': ['mean', 'count'],
                '专利增长率': 'mean',
                'treatment': 'count'
            }).round(2)
            province_stats.to_excel(writer, sheet_name='按省份统计')
        
        print(f"   - Excel文件已保存: {output_filename}")
        
        return {
            'timeline_df': timeline_df,
            'excel_file': output_filename,
            'total_companies': len(timeline_df),
            'companies_with_province': len(timeline_df) - missing_province,
            'missing_province': missing_province
        }
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_province(region):
    """
    从地区字符串中提取省份名
    """
    if pd.isna(region) or region == '':
        return None
    
    # 地区格式通常是: "中国|省份|城市|区县"
    parts = str(region).split('|')
    
    if len(parts) >= 2:
        # 第二个部分通常是省份
        province = parts[1]
        
        # 清理省份名称
        province = province.strip()
        
        # 处理一些特殊情况
        if province in ['中国']:
            # 如果第二个是"中国"，尝试第三个
            if len(parts) >= 3:
                province = parts[2]
            else:
                return None
        
        return province
    
    return None

def add_province_gdp_data():
    """
    添加投资前三年，后三年所在省份的gdp数据
    """
    try:
        print("=== 添加省份GDP数据 ===")
        
        # 1. 读取带省份信息的timeline数据
        print("1. 读取带省份信息的数据...")
        timeline_df = pd.read_excel('regress_data_with_province.xlsx', sheet_name='投资前后专利数据')
        print(f"   - 数据行数: {len(timeline_df):,}")
        
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
            company = row['公司名称']
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
        
        # 6. 计算GDP统计信息
        print("\n6. GDP数据统计:")
        gdp_columns = [col for col in timeline_df.columns if 'GDP' in col and 'ln' not in col]
        
        for col in gdp_columns:
            non_zero_count = (timeline_df[col] > 0).sum()
            if non_zero_count > 0:
                mean_gdp = timeline_df[col][timeline_df[col] > 0].mean()
                print(f"   - {col}: 非零值数量 {non_zero_count:,}, 平均值 {mean_gdp:.2f}亿元")
        
        # 7. 保存更新后的数据
        print("\n7. 保存更新后的数据...")
        output_filename = 'regress_data_with_gdp.xlsx'
        
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
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
            
            # 按省份统计
            province_stats = timeline_df.groupby('省份').agg({
                '前3年专利总数': ['mean', 'count'],
                '后3年专利总数': ['mean', 'count'],
                '专利增长率': 'mean',
                'treatment': 'count'
            }).round(2)
            province_stats.to_excel(writer, sheet_name='按省份统计')
            
            # GDP统计
            gdp_stats = timeline_df[gdp_columns].describe()
            gdp_stats.to_excel(writer, sheet_name='GDP统计')
        
        print(f"   - Excel文件已保存: {output_filename}")

        
        # 8. 显示一些示例数据
        print(f"\n8. 数据示例（前3行）:")
        sample_cols = ['公司名称', '投资年份', '省份', '前3年GDP_前1年', '投资当年GDP', '后3年GDP_后1年']
        print(timeline_df[sample_cols].head(3))
        
        return {
            'timeline_df': timeline_df,
            'excel_file': output_filename,
            'total_companies': len(timeline_df),
            'gdp_matched_count': matched_count,
            'gdp_total_attempts': total_attempts,
            'gdp_match_rate': matched_count / total_attempts * 100
        }
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 提取公司所在省份信息
    result = extract_province_from_region()
    
    # 添加省份GDP数据
    result = add_province_gdp_data()
    
    if result:
        print(f"\n=== 处理完成 ===")
        print(f"数据文件: {result['excel_file']}")
        print(f"总公司数: {result['total_companies']:,}")
        print(f"GDP数据匹配率: {result['gdp_match_rate']:.2f}%")
        print(f"\n建议查看Excel文件，包含以下sheet:")
        print(f"1. 投资前后专利数据 - 主要数据（含省份和GDP信息）")
        print(f"2. 数据统计 - 描述性统计")
        print(f"3. 按年份统计 - 年度汇总")
        print(f"4. 按省份统计 - 省份汇总")
        print(f"5. GDP统计 - GDP数据统计")
