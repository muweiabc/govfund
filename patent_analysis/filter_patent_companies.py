import pandas as pd
import numpy as np
from datetime import datetime

def filter_patent_companies():
    """
    选取invest中有专利公司首次投资，根据投资时间的年份在patent_company_yearly中查找，
    排除掉在投资前后三年都没有专利的公司
    """
    try:
        print("=== 开始筛选有专利的公司 ===")
        
        # 1. 读取数据
        print("1. 读取数据文件...")
        invest_df = pd.read_excel('invest.xlsx')
        patent_df = pd.read_excel('company_patent_yearly.xlsx')
        
        print(f"   - invest.xlsx: {len(invest_df):,} 行")
        print(f"   - company_patent_yearly.xlsx: {len(patent_df):,} 行")
        
        # 2. 数据预处理
        print("\n2. 数据预处理...")
        
        # 重命名专利数据的第一列为公司名称
        patent_df = patent_df.rename(columns={'Unnamed: 0': '公司名称'})
        
        # 处理投资时间，提取年份
        print("   - 处理投资时间...")
        invest_df['投资年份'] = pd.to_datetime(invest_df['投资时间'], errors='coerce').dt.year
        
        # 删除投资时间为空的行
        invest_df = invest_df.dropna(subset=['投资年份'])
        print(f"   - 有效投资记录: {len(invest_df):,} 行")
        
        # 3. 筛选有专利的公司
        print("\n3. 筛选有专利的公司...")
        
        # 获取专利数据中的公司名称列表
        patent_companies = set(patent_df['公司名称'].dropna())
        print(f"   - 专利数据中的公司数量: {len(patent_companies):,}")
        
        # 筛选invest中在专利数据中存在的公司
        invest_with_patent = invest_df[invest_df['企业'].isin(patent_companies)].copy()
        print(f"   - 有专利记录的投资记录: {len(invest_with_patent):,} 行")
        
        # 4. 筛选首次投资
        print("\n4. 筛选首次投资...")
        
        # 按公司和投资年份排序，取每个公司的第一次投资
        invest_with_patent = invest_with_patent.sort_values(['企业', '投资年份'])
        first_investments = invest_with_patent.drop_duplicates(subset=['企业'], keep='first')
        print(f"   - 首次投资记录: {len(first_investments):,} 行")
        
        # 5. 检查投资前后三年的专利情况
        print("\n5. 检查投资前后三年的专利情况...")
        
        valid_companies = []
        excluded_companies = []
        
        for idx, row in first_investments.iterrows():
            company = row['企业']
            investment_year = row['投资年份']
            
            # 在专利数据中查找该公司
            company_patent_data = patent_df[patent_df['公司名称'] == company]
            
            if len(company_patent_data) == 0:
                excluded_companies.append({
                    '公司名称': company,
                    '投资年份': investment_year,
                    '排除原因': '专利数据中未找到'
                })
                continue
            
            # 获取投资前后三年的专利数据
            pre_years = [investment_year - 3, investment_year - 2, investment_year - 1]
            post_years = [investment_year + 1, investment_year + 2, investment_year + 3]
            
            # 检查前三年是否有专利
            pre_patents = []
            for year in pre_years:
                if str(year) in company_patent_data.columns:
                    patent_count = company_patent_data[str(year)].iloc[0]
                    pre_patents.append(patent_count)
                else:
                    pre_patents.append(0)
            
            # 检查后三年是否有专利
            post_patents = []
            for year in post_years:
                if str(year) in company_patent_data.columns:
                    patent_count = company_patent_data[str(year)].iloc[0]
                    post_patents.append(patent_count)
                else:
                    post_patents.append(0)
            
            # 判断是否前后三年都没有专利
            pre_has_patent = any(patent > 0 for patent in pre_patents)
            post_has_patent = any(patent > 0 for patent in post_patents)
            
            if not pre_has_patent and not post_has_patent:
                excluded_companies.append({
                    '公司名称': company,
                    '投资年份': investment_year,
                    '前三年专利数': pre_patents,
                    '后三年专利数': post_patents,
                    '排除原因': '投资前后三年都没有专利'
                })
            else:
                valid_companies.append({
                    '公司名称': company,
                    '投资年份': investment_year,
                    '前三年专利数': pre_patents,
                    '后三年专利数': post_patents,
                    '前三年总专利数': sum(pre_patents),
                    '后三年总专利数': sum(post_patents),
                    '投资当年专利数': company_patent_data[str(investment_year)].iloc[0] if str(investment_year) in company_patent_data.columns else 0
                })
        
        print(f"   - 符合条件的公司: {len(valid_companies):,} 个")
        print(f"   - 被排除的公司: {len(excluded_companies):,} 个")
        
        # 6. 创建结果数据框
        print("\n6. 创建结果数据框...")
        
        valid_df = pd.DataFrame(valid_companies)
        excluded_df = pd.DataFrame(excluded_companies)
        
        # 7. 统计信息
        print("\n7. 统计信息...")
        
        if len(valid_df) > 0:
            print(f"   - 投资年份范围: {valid_df['投资年份'].min()} - {valid_df['投资年份'].max()}")
            print(f"   - 前三年平均专利数: {valid_df['前三年总专利数'].mean():.2f}")
            print(f"   - 后三年平均专利数: {valid_df['后三年总专利数'].mean():.2f}")
            print(f"   - 投资当年平均专利数: {valid_df['投资当年专利数'].mean():.2f}")
            
            # 按投资年份分组统计
            year_stats = valid_df.groupby('投资年份').agg({
                '公司名称': 'count',
                '前三年总专利数': 'mean',
                '后三年总专利数': 'mean',
                '投资当年专利数': 'mean'
            }).round(2)
            
            print(f"\n   按投资年份统计:")
            print(year_stats)
        
        # 8. 保存结果
        print("\n8. 保存结果...")
        
        output_filename = 'filtered_patent_companies.xlsx'
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            valid_df.to_excel(writer, sheet_name='符合条件的公司', index=False)
            excluded_df.to_excel(writer, sheet_name='被排除的公司', index=False)
            
            # 保存统计信息
            if len(valid_df) > 0:
                year_stats.to_excel(writer, sheet_name='按年份统计')
        
        print(f"   - 结果已保存: {output_filename}")
        
        return {
            'valid_companies': valid_df,
            'excluded_companies': excluded_df,
            'output_file': output_filename
        }
        
    except Exception as e:
        print(f"筛选过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = filter_patent_companies()
    
    if result:
        print(f"\n=== 筛选完成 ===")
        print(f"符合条件的公司: {len(result['valid_companies']):,} 个")
        print(f"被排除的公司: {len(result['excluded_companies']):,} 个")
        print(f"结果文件: {result['output_file']}")
    else:
        print("筛选失败")
