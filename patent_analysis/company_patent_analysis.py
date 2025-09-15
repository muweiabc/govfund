import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
import pickle
import time
from tqdm import tqdm

def analyze_company_patents(output_file, patent_file):
    """
    读取invest中的公司名，在t'ri'm'pa't'e'n't中查找该公司在各年份获得的专利数量
    使用稀疏矩阵存储结果，避免内存浪费
    """
    print("开始分析公司专利数据...")
    
    # 1. 读取filtered_companies数据
    print("invest.csv...")
    companies_df = pd.read_excel('invest.xlsx', sheet_name='有专利公司首次投资')
    company_names = companies_df['融资主体'].tolist()
    print(f"共读取到 {len(company_names)} 家公司")
    
    # 2. 读取专利数据（分块读取以节省内存）
    print(f"正在读取{patent_file}...")
    
    # 获取文件大小以估算行数
    import os
    file_size = os.path.getsize(patent_file)
    print(f"文件大小: {file_size / (1024**3):.2f} GB")
    
    # 分块读取专利数据
    chunk_size = 1000000  # 每次读取100万行
    patents_chunks = []
    
    for chunk in tqdm(pd.read_csv(patent_file, chunksize=chunk_size), 
                      desc="读取专利数据"):
        # 只保留需要的列
        patents_chunks.append(chunk.copy())
    
    patents_df = pd.concat(patents_chunks, ignore_index=True)
    print(f"专利数据总行数: {len(patents_df)}")
    
    # 3. 数据预处理
    print("正在预处理数据...")
    
    # 处理申请年份，提取年份
    patents_df['申请年份'] = pd.to_numeric(patents_df['申请年份'], errors='coerce')
    patents_df = patents_df.dropna(subset=['申请年份'])
    patents_df['申请年份'] = patents_df['申请年份'].astype(int)
    
    # 获取年份范围
    years = sorted(patents_df['申请年份'].unique().astype(int))
    print(f"专利申请年份范围: {min(years)} - {max(years)}")
    
    # 4. 创建公司名称到索引的映射
    company_to_idx = {company: idx for idx, company in enumerate(company_names)}
    year_to_idx = {year: idx for idx, year in enumerate(years)}
    
    # 5. 初始化稀疏矩阵
    print("正在创建稀疏矩阵...")
    
    
    # 6. 统计每个公司在每年的专利数量
    print("正在统计专利数量...")
    start_time = time.time()
    
    APPLICANT = '申请人'
    YEAR = '申请年份'
    PATENT_COUNT = '专利数量'
    CITATION_COUNT = '被引证次数'
    INVENTING_COUNT = '发明数量'
    INVENTING_CITATION = '发明被引证次数'

    # 按公司分组统计
    # patents_df['被引证次数'] = patents_df['被引证次数'].fillna(0)
    patents_df['被引证次数'] = pd.to_numeric(patents_df['被引证次数'], errors='coerce').fillna(0).astype(float)
    # patents_df['被引证次数'] = patents_df['被引证次数'].astype(int)
    
    company_patents = patents_df.groupby([APPLICANT, YEAR])['被引证次数'].agg(["count",'sum'])
    company_patents = company_patents.rename(columns={'count':PATENT_COUNT,'sum':CITATION_COUNT}).reset_index()  # 每组数量
    
    years_str = ['y' + str(year) for year in years]

    # 7. 创建稀疏矩阵
    print("正在构建稀疏矩阵...")
    rows, cols, data_count, data_citation = [], [], [], []
    for _, row in tqdm(company_patents.iterrows(), total=len(company_patents), desc="处理专利数据"):
        
        company = row[APPLICANT]
        year = row[YEAR]
        count = row[PATENT_COUNT] 
        citations = row[CITATION_COUNT]

        # 如果公司在我们的列表中
        if company in company_to_idx:
            company_idx = company_to_idx[company]
            year_idx = year_to_idx[year]
            
            rows.append(company_idx)
            cols.append(year_idx)
            data_count.append(count)
            data_citation.append(citations)
      
    
    sparse_matrix = csr_matrix((data_count, (rows, cols)), 
                              shape=(len(company_names), len(years)))
    count_df = pd.DataFrame(
        sparse_matrix.toarray(),
        index=company_names,
        columns=years_str
    )
    
    sparse_matrix = csr_matrix((data_citation, (rows, cols)), 
                              shape=(len(company_names), len(years)))
    citation_df = pd.DataFrame(
            sparse_matrix.toarray(),
            index=company_names,
            columns=years_str
        )

    #  处理发明数据

    company_invention_df = patents_df[(patents_df['专利类型'] == '发明专利') | (patents_df['专利类型'] == '发明申请')]
    company_inventing = company_invention_df.groupby([APPLICANT, YEAR])['被引证次数'].agg(["count",'sum'])
    company_inventing = company_inventing.rename(columns={'count':INVENTING_COUNT,'sum':INVENTING_CITATION}).reset_index()
    
    rows, cols, invention_count, invention_citation = [], [], [],[]
    for _, row in tqdm(company_inventing.iterrows(), total=len(company_inventing), desc="处理发明数据"):
        company = row[APPLICANT]
        year = row[YEAR]
        count = row[INVENTING_COUNT] 
        citations = row[INVENTING_CITATION]
        # 如果公司在我们的列表中
        if company in company_to_idx:
            company_idx = company_to_idx[company]
            year_idx = year_to_idx[year]
            
            rows.append(company_idx)
            cols.append(year_idx)
            invention_count.append(count)
            invention_citation.append(citations)

    sparse_matrix = csr_matrix((invention_count, (rows, cols)), 
                              shape=(len(company_names), len(years)))
    company_invention_df = pd.DataFrame(
            sparse_matrix.toarray(),
            index=company_names,
            columns=years_str
        )

    sparse_matrix = csr_matrix((invention_citation, (rows, cols)), 
                              shape=(len(company_names), len(years)))
    invention_citation_df = pd.DataFrame(
            sparse_matrix.toarray(),
            index=company_names,
            columns=years_str
        )

    with pd.ExcelWriter(output_file) as writer:
        count_df.to_excel(writer, sheet_name=PATENT_COUNT)
        citation_df.to_excel(writer, sheet_name=CITATION_COUNT)
        company_invention_df.to_excel(writer, sheet_name=INVENTING_COUNT)
        invention_citation_df.to_excel(writer, sheet_name=INVENTING_CITATION)
    
    # 9. 输出统计信息
    print("\n=== 分析结果 ===")
    print(f"公司数量: {len(company_names)}")
    print(f"年份数量: {len(years)}")
    print(f"稀疏矩阵形状: {sparse_matrix.shape}")
    print(f"非零元素数量: {sparse_matrix.nnz}")
    print(f"稀疏度: {(1 - sparse_matrix.nnz / (len(company_names) * len(years))) * 100:.2f}%")
    
  
    
    print(f"\n分析完成，耗时: {time.time() - start_time:.2f} 秒")
    print("结果已保存到:")
    print(output_file)
    
    return sparse_matrix, company_names, years

def load_and_query_results():
    """
    加载保存的结果并进行查询
    """
    try:
        with open('company_patent_matrix.pkl', 'rb') as f:
            data = pickle.load(f)
        
        sparse_matrix = data['sparse_matrix']
        company_names = data['company_names']
        years = data['years']
        
        print("结果加载成功!")
        print(f"矩阵形状: {sparse_matrix.shape}")
        
        # 查询特定公司的专利情况
        query_company = "北京蓝晶微生物科技有限公司"
        if query_company in company_names:
            company_idx = company_names.index(query_company)
            patents_by_year = sparse_matrix[company_idx].toarray().flatten()
            
            print(f"\n{query_company} 的专利情况:")
            for year, count in zip(years, patents_by_year):
                if count > 0:
                    print(f"  {year}年: {int(count)}件")
        
        return sparse_matrix, company_names, years
        
    except FileNotFoundError:
        print("未找到保存的结果文件，请先运行分析")
        return None, None, None

def query_company_patents(company_name):
    """
    查询特定公司的专利情况
    """
    try:
        with open('company_patent_matrix.pkl', 'rb') as f:
            data = pickle.load(f)
        
        sparse_matrix = data['sparse_matrix']
        company_names = data['company_names']
        years = data['years']
        
        if company_name in company_names:
            company_idx = company_names.index(company_name)
            patents_by_year = sparse_matrix[company_idx].toarray().flatten()
            
            print(f"\n{company_name} 的专利情况:")
            total_patents = 0
            for year, count in zip(years, patents_by_year):
                if count > 0:
                    print(f"  {year}年: {int(count)}件")
                    total_patents += count
            
            print(f"总计: {total_patents}件专利")
            return patents_by_year
        else:
            print(f"未找到公司: {company_name}")
            return None
            
    except FileNotFoundError:
        print("未找到保存的结果文件，请先运行分析")
        return None

if __name__ == "__main__":
    # 运行分析
    # sparse_matrix, company_names, years = analyze_company_patents()
    import argparse
    parser = argparse.ArgumentParser(description='公司专利分析')
    
    # 基本参数
    
    parser.add_argument('--output_file', 
                       default='patent_analysis/company_patent_yearly.xlsx',
                       help='输出文件路径')
    parser.add_argument('--patent_file', 
                       default='data/trimpatent_all.csv',
                       help='专利数据文件路径')
    args = parser.parse_args()
    analyze_company_patents(args.output_file, args.patent_file)
    # print("演示查询功能:")
    # load_and_query_results()
    
    # # 查询特定公司
    # print("\n" + "="*50)
    # print("查询特定公司专利:")
    # query_company_patents("北京蓝晶微生物科技有限公司")
