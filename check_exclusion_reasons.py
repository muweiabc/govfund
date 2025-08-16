import pandas as pd
import numpy as np

def check_exclusion_reasons():
    """
    检查为什么所有公司都被排除
    """
    try:
        print("=== 检查排除原因 ===")
        
        # 1. 读取数据
        print("1. 读取数据文件...")
        invest_df = pd.read_excel('invest.xlsx')
        patent_df = pd.read_excel('company_patent_yearly.xlsx')
        
        # 重命名专利数据的第一列为公司名称
        patent_df = patent_df.rename(columns={'Unnamed: 0': '公司名称'})
        
        # 处理投资时间，提取年份
        invest_df['投资年份'] = pd.to_datetime(invest_df['投资时间'], errors='coerce').dt.year
        invest_df = invest_df.dropna(subset=['投资年份'])
        
        # 筛选有专利的公司
        patent_companies = set(patent_df['公司名称'].dropna())
        invest_with_patent = invest_df[invest_df['企业'].isin(patent_companies)].copy()
        
        # 筛选首次投资
        invest_with_patent = invest_with_patent.sort_values(['企业', '投资年份'])
        first_investments = invest_with_patent.drop_duplicates(subset=['企业'], keep='first')
        
        print(f"   - 首次投资记录: {len(first_investments):,} 行")
        
        # 2. 检查专利数据的年份范围
        print("\n2. 检查专利数据的年份范围...")
        year_columns = [col for col in patent_df.columns if col.isdigit()]
        print(f"   - 专利数据年份范围: {min(year_columns)} - {max(year_columns)}")
        
        # 3. 检查投资年份分布
        print("\n3. 检查投资年份分布...")
        print(f"   - 投资年份范围: {first_investments['投资年份'].min()} - {first_investments['投资年份'].max()}")
        
        # 4. 详细检查几个样本
        print("\n4. 详细检查样本...")
        
        sample_companies = first_investments.head(5)
        
        for idx, row in sample_companies.iterrows():
            company = row['企业']
            investment_year = row['投资年份']
            
            print(f"\n   公司: {company}")
            print(f"   投资年份: {investment_year}")
            
            # 在专利数据中查找该公司
            company_patent_data = patent_df[patent_df['公司名称'] == company]
            
            if len(company_patent_data) == 0:
                print(f"   - 专利数据中未找到")
                continue
            
            # 获取投资前后三年的专利数据
            pre_years = [investment_year - 3, investment_year - 2, investment_year - 1]
            post_years = [investment_year + 1, investment_year + 2, investment_year + 3]
            
            print(f"   - 前三年: {pre_years}")
            print(f"   - 后三年: {post_years}")
            
            # 检查前三年是否有专利
            pre_patents = []
            for year in pre_years:
                if str(year) in company_patent_data.columns:
                    patent_count = company_patent_data[str(year)].iloc[0]
                    pre_patents.append(patent_count)
                    print(f"     {year}年: {patent_count} 专利")
                else:
                    pre_patents.append(0)
                    print(f"     {year}年: 无数据")
            
            # 检查后三年是否有专利
            post_patents = []
            for year in post_years:
                if str(year) in company_patent_data.columns:
                    patent_count = company_patent_data[str(year)].iloc[0]
                    post_patents.append(patent_count)
                    print(f"     {year}年: {patent_count} 专利")
                else:
                    post_patents.append(0)
                    print(f"     {year}年: 无数据")
            
            # 判断是否前后三年都没有专利
            pre_has_patent = any(patent > 0 for patent in pre_patents)
            post_has_patent = any(patent > 0 for patent in post_patents)
            
            print(f"   - 前三年有专利: {pre_has_patent}")
            print(f"   - 后三年有专利: {post_has_patent}")
            print(f"   - 是否被排除: {not pre_has_patent and not post_has_patent}")
        
        # 5. 统计投资年份分布
        print("\n5. 投资年份分布统计...")
        year_distribution = first_investments['投资年份'].value_counts().sort_index()
        print(year_distribution.head(10))
        print("...")
        print(year_distribution.tail(10))
        
        # 6. 检查年份匹配问题
        print("\n6. 检查年份匹配问题...")
        
        # 检查有多少投资年份在专利数据范围内
        min_patent_year = int(min(year_columns))
        max_patent_year = int(max(year_columns))
        
        valid_year_investments = first_investments[
            (first_investments['投资年份'] >= min_patent_year) & 
            (first_investments['投资年份'] <= max_patent_year)
        ]
        
        print(f"   - 投资年份在专利数据范围内的记录: {len(valid_year_investments):,} 行")
        
        # 检查这些记录中前后三年是否都有数据
        valid_companies_count = 0
        
        for idx, row in valid_year_investments.iterrows():
            company = row['企业']
            investment_year = row['投资年份']
            
            company_patent_data = patent_df[patent_df['公司名称'] == company]
            
            if len(company_patent_data) == 0:
                continue
            
            # 获取投资前后三年的专利数据
            pre_years = [investment_year - 3, investment_year - 2, investment_year - 1]
            post_years = [investment_year + 1, investment_year + 2, investment_year + 3]
            
            # 检查前三年是否有数据
            pre_has_data = all(str(year) in company_patent_data.columns for year in pre_years)
            post_has_data = all(str(year) in company_patent_data.columns for year in post_years)
            
            if pre_has_data and post_has_data:
                valid_companies_count += 1
        
        print(f"   - 前后三年都有数据的公司: {valid_companies_count:,} 个")
        
    except Exception as e:
        print(f"检查过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_exclusion_reasons()
