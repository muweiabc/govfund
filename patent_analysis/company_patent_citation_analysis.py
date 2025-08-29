import pandas as pd
import numpy as np
import pickle
import time
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

def analyze_company_patent_citations():
    """
    读取data/trimpatent_all.csv文件，选出其中申请人在invest.xlsx的融资主体里的行，
    按年计算该公司的每年的专利的被引证次数
    """
    print("开始分析公司专利被引证次数...")
    
    # 1. 读取invest.xlsx中的融资主体数据
    print("正在读取invest.xlsx...")
    try:
        invest_df = pd.read_excel('invest.xlsx')
        company_names = invest_df['融资主体'].dropna().unique().tolist()
        print(f"共读取到 {len(company_names)} 家融资主体公司")
    except Exception as e:
        print(f"读取invest.xlsx失败: {e}")
        return None, None, None
    
    # 2. 读取专利数据（分块读取以节省内存）
    print("正在读取data/trimpatent_all.csv...")
    
    # 获取文件大小以估算行数
    import os
    file_path = 'data/trimpatent_all.csv'
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None, None, None
    
    file_size = os.path.getsize(file_path)
    print(f"文件大小: {file_size / (1024**3):.2f} GB")
    
    # 分块读取专利数据，只保留需要的列
    chunk_size = 100000  # 每次读取10万行
    patents_chunks = []
    
    try:
        for chunk in tqdm(pd.read_csv(file_path, chunksize=chunk_size, encoding='utf-8'), 
                          desc="读取专利数据"):
            # 只保留需要的列：申请人、申请年份、被引证次数
            if '申请人' in chunk.columns and '申请年份' in chunk.columns:
                # 检查是否有被引证次数列
                citation_col = None
                for col in chunk.columns:
                    if '被引证' in col or '引证' in col:
                        citation_col = col
                        break
                
                if citation_col:
                    chunk = chunk[['申请人', '申请年份', citation_col]].copy()
                    chunk.columns = ['申请人', '申请年份', '被引证次数']
                else:
                    # 如果没有找到被引证次数列，创建一个默认的0值列
                    chunk = chunk[['申请人', '申请年份']].copy()
                    chunk['被引证次数'] = 0
                
                patents_chunks.append(chunk)
            else:
                print(f"警告：chunk中缺少必要的列，列名: {chunk.columns.tolist()}")
                continue
                
    except Exception as e:
        print(f"读取专利数据失败: {e}")
        # 尝试不同的编码
        try:
            print("尝试使用gbk编码...")
            for chunk in tqdm(pd.read_csv(file_path, chunksize=chunk_size, encoding='gbk'), 
                              desc="读取专利数据"):
                if '申请人' in chunk.columns and '申请年份' in chunk.columns:
                    citation_col = None
                    for col in chunk.columns:
                        if '被引证' in col or '引证' in col:
                            citation_col = col
                            break
                    
                    if citation_col:
                        chunk = chunk[['申请人', '申请年份', citation_col]].copy()
                        chunk.columns = ['申请人', '申请年份', '被引证次数']
                    else:
                        chunk = chunk[['申请人', '申请年份']].copy()
                        chunk['被引证次数'] = 0
                    
                    patents_chunks.append(chunk)
        except Exception as e2:
            print(f"使用gbk编码也失败: {e2}")
            return None, None, None
    
    if not patents_chunks:
        print("没有成功读取到专利数据")
        return None, None, None
    
    patents_df = pd.concat(patents_chunks, ignore_index=True)
    print(f"专利数据总行数: {len(patents_df)}")
    
    # 3. 数据预处理
    print("正在预处理数据...")
    
    # 处理申请年份，提取年份
    patents_df['申请年份'] = pd.to_numeric(patents_df['申请年份'], errors='coerce')
    patents_df = patents_df.dropna(subset=['申请年份'])
    patents_df['申请年份'] = patents_df['申请年份'].astype(int)
    
    # 处理被引证次数
    patents_df['被引证次数'] = pd.to_numeric(patents_df['被引证次数'], errors='coerce').fillna(0).astype(int)
    
    # 获取年份范围
    years = sorted(patents_df['申请年份'].unique())
    print(f"专利申请年份范围: {min(years)} - {max(years)}")
    
    # 4. 筛选出融资主体公司的专利
    print("正在筛选融资主体公司的专利...")
    company_patents = patents_df[patents_df['申请人'].isin(company_names)].copy()
    print(f"融资主体公司专利数量: {len(company_patents)}")
    
    # 5. 按公司和年份分组，计算每年的被引证次数总和
    print("正在计算每年的被引证次数...")
    company_citations_by_year = company_patents.groupby(['申请人', '申请年份'])['被引证次数'].sum().reset_index()
    
    # 6. 创建年度被引证次数矩阵
    print("正在创建年度被引证次数矩阵...")
    
    # 创建透视表，行为公司，列为年份，值为被引证次数
    result_df = company_citations_by_year.pivot_table(
        index='申请人', 
        columns='申请年份', 
        values='被引证次数', 
        fill_value=0
    )
    
    # 确保所有公司都在结果中（即使没有专利）
    missing_companies = set(company_names) - set(result_df.index)
    if missing_companies:
        # 为缺失的公司添加0值行
        for company in missing_companies:
            result_df.loc[company] = 0
    
    # 确保所有年份都在结果中
    missing_years = set(years) - set(result_df.columns)
    if missing_years:
        # 为缺失的年份添加0值列
        for year in missing_years:
            result_df[year] = 0
    
    # 重新排序，确保公司顺序和年份顺序一致
    result_df = result_df.reindex(index=company_names, columns=years, fill_value=0)
    
    # 7. 保存结果
    print("正在保存结果...")
    
    # 保存为Excel格式（便于查看）
    result_df.to_excel('company_patent_citations_yearly.xlsx', sheet_name='被引证次数')
    
    # 保存为pickle格式（便于后续分析）
    with open('company_patent_citations_data.pkl', 'wb') as f:
        pickle.dump({
            'result_df': result_df,
            'company_names': company_names,
            'years': years,
            'citation_data': company_citations_by_year
        }, f)
    
    # 8. 输出统计信息
    print("\n=== 分析结果 ===")
    print(f"公司数量: {len(company_names)}")
    print(f"年份数量: {len(years)}")
    print(f"数据矩阵形状: {result_df.shape}")
    
    # 计算非零元素数量和稀疏度
    non_zero_count = (result_df != 0).sum().sum()
    total_elements = len(company_names) * len(years)
    sparsity = (1 - non_zero_count / total_elements) * 100
    print(f"非零元素数量: {non_zero_count}")
    print(f"稀疏度: {sparsity:.2f}%")
    
    # 显示一些示例
    print("\n=== 示例数据 ===")
    print("前5家公司的被引证情况:")
    for i in range(min(5, len(company_names))):
        company = company_names[i]
        citations_by_year = result_df.iloc[i]
        total_citations = citations_by_year.sum()
        print(f"{company}: 总计被引证 {total_citations} 次")
        # 显示有被引证的年份
        years_with_citations = citations_by_year[citations_by_year > 0]
        if len(years_with_citations) > 0:
            print(f"  有被引证的年份: {dict(years_with_citations)}")
    
    print(f"\n分析完成！")
    print("结果已保存到:")
    print("- company_patent_citations_data.pkl (Python对象)")
    print("- company_patent_citations_yearly.xlsx (Excel格式)")
    
    return result_df, company_names, years

def query_company_citations(company_name):
    """
    查询特定公司的专利被引证情况
    """
    try:
        with open('company_patent_citations_data.pkl', 'rb') as f:
            data = pickle.load(f)
        
        result_df = data['result_df']
        company_names = data['company_names']
        years = data['years']
        
        if company_name in company_names:
            citations_by_year = result_df.loc[company_name]
            
            print(f"\n{company_name} 的专利被引证情况:")
            total_citations = 0
            for year, citations in citations_by_year.items():
                if citations > 0:
                    print(f"  {year}年: {int(citations)}次被引证")
                    total_citations += citations
            
            print(f"总计被引证: {total_citations}次")
            return citations_by_year
        else:
            print(f"未找到公司: {company_name}")
            return None
            
    except FileNotFoundError:
        print("未找到保存的结果文件，请先运行分析")
        return None

def get_top_cited_companies(top_n=10):
    """
    获取被引证次数最多的前N家公司
    """
    try:
        with open('company_patent_citations_data.pkl', 'rb') as f:
            data = pickle.load(f)
        
        result_df = data['result_df']
        company_names = data['company_names']
        
        # 计算每个公司的总被引证次数
        total_citations = result_df.sum(axis=1)
        
        # 创建公司-被引证次数的DataFrame
        company_citations_df = pd.DataFrame({
            '公司名称': company_names,
            '总被引证次数': total_citations
        })
        
        # 按被引证次数排序
        top_companies = company_citations_df.nlargest(top_n, '总被引证次数')
        
        print(f"\n被引证次数最多的前{top_n}家公司:")
        for idx, row in top_companies.iterrows():
            print(f"{row['公司名称']}: {int(row['总被引证次数'])}次被引证")
        
        return top_companies
        
    except FileNotFoundError:
        print("未找到保存的结果文件，请先运行分析")
        return None

if __name__ == "__main__":
    # 运行分析
    print("开始分析公司专利被引证次数...")
    result_df, company_names, years = analyze_company_patent_citations()
    
    if result_df is not None:
        # 演示查询功能
        print("\n" + "="*50)
        print("演示查询功能:")
        
        # 查询特定公司
        print("\n" + "="*50)
        print("查询特定公司被引证情况:")
        if company_names:
            query_company_citations(company_names[0])
        
        # 获取被引证最多的公司
        print("\n" + "="*50)
        print("获取被引证最多的公司:")
        get_top_cited_companies(10)
    else:
        print("分析失败，请检查数据文件")
