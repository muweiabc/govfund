import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
import pickle
import time
from tqdm import tqdm

def analyze_company_patents():
    """
    读取filtered_companies中的公司名，在t'ri'm'pa't'e'n't中查找该公司在各年份获得的专利数量
    使用稀疏矩阵存储结果，避免内存浪费
    """
    print("开始分析公司专利数据...")
    
    # 1. 读取filtered_companies数据
    print("正在读取filtered_companies.csv...")
    companies_df = pd.read_csv('filtered_companies.csv')
    company_names = companies_df['融资主体'].tolist()
    print(f"共读取到 {len(company_names)} 家公司")
    
    # 2. 读取专利数据（分块读取以节省内存）
    print("正在读取trimpatent_all.csv...")
    
    # 获取文件大小以估算行数
    import os
    file_size = os.path.getsize('trimpatent_all.csv')
    print(f"文件大小: {file_size / (1024**3):.2f} GB")
    
    # 分块读取专利数据
    chunk_size = 100000  # 每次读取10万行
    patents_chunks = []
    
    for chunk in tqdm(pd.read_csv('trimpatent_all.csv', chunksize=chunk_size), 
                      desc="读取专利数据"):
        # 只保留需要的列
        chunk = chunk[['申请人', '申请年份']].copy()
        patents_chunks.append(chunk)
    
    patents_df = pd.concat(patents_chunks, ignore_index=True)
    print(f"专利数据总行数: {len(patents_df)}")
    
    # 3. 数据预处理
    print("正在预处理数据...")
    
    # 处理申请年份，提取年份
    patents_df['申请年份'] = pd.to_numeric(patents_df['申请年份'], errors='coerce')
    patents_df = patents_df.dropna(subset=['申请年份'])
    patents_df['申请年份'] = patents_df['申请年份'].astype(int)
    
    # 获取年份范围
    years = sorted(patents_df['申请年份'].unique())
    print(f"专利申请年份范围: {min(years)} - {max(years)}")
    
    # 4. 创建公司名称到索引的映射
    company_to_idx = {company: idx for idx, company in enumerate(company_names)}
    year_to_idx = {year: idx for idx, year in enumerate(years)}
    
    # 5. 初始化稀疏矩阵
    print("正在创建稀疏矩阵...")
    rows, cols, data = [], [], []
    
    # 6. 统计每个公司在每年的专利数量
    print("正在统计专利数量...")
    start_time = time.time()
    
    # 按公司分组统计
    company_patents = patents_df.groupby(['申请人', '申请年份']).size().reset_index(name='专利数量')
    
    print("正在构建稀疏矩阵数据...")
    for _, row in tqdm(company_patents.iterrows(), total=len(company_patents), desc="处理专利数据"):
        company = row['申请人']
        year = row['申请年份']
        count = row['专利数量']
        
        # 如果公司在我们的列表中
        if company in company_to_idx:
            company_idx = company_to_idx[company]
            year_idx = year_to_idx[year]
            
            rows.append(company_idx)
            cols.append(year_idx)
            data.append(count)
    
    # 7. 创建稀疏矩阵
    print("正在构建稀疏矩阵...")
    sparse_matrix = csr_matrix((data, (rows, cols)), 
                              shape=(len(company_names), len(years)))
    
    # 8. 保存结果
    print("正在保存结果...")
    
    # 保存稀疏矩阵
    with open('company_patent_matrix.pkl', 'wb') as f:
        pickle.dump({
            'sparse_matrix': sparse_matrix,
            'company_names': company_names,
            'years': years,
            'company_to_idx': company_to_idx,
            'year_to_idx': year_to_idx
        }, f)
    
    # 保存为CSV格式（便于查看）
    print("正在保存CSV格式...")
    result_df = pd.DataFrame(
        sparse_matrix.toarray(),
        index=company_names,
        columns=years
    )
    result_df.to_csv('company_patent_yearly.csv')
    
    # 9. 输出统计信息
    print("\n=== 分析结果 ===")
    print(f"公司数量: {len(company_names)}")
    print(f"年份数量: {len(years)}")
    print(f"稀疏矩阵形状: {sparse_matrix.shape}")
    print(f"非零元素数量: {sparse_matrix.nnz}")
    print(f"稀疏度: {(1 - sparse_matrix.nnz / (len(company_names) * len(years))) * 100:.2f}%")
    
    # 显示一些示例
    print("\n=== 示例数据 ===")
    print("前5家公司的专利情况:")
    for i in range(min(5, len(company_names))):
        company = company_names[i]
        patents_by_year = result_df.iloc[i]
        total_patents = patents_by_year.sum()
        print(f"{company}: 总计 {total_patents} 件专利")
        # 显示有专利的年份
        years_with_patents = patents_by_year[patents_by_year > 0]
        if len(years_with_patents) > 0:
            print(f"  有专利的年份: {dict(years_with_patents)}")
    
    print(f"\n分析完成，耗时: {time.time() - start_time:.2f} 秒")
    print("结果已保存到:")
    print("- company_patent_matrix.pkl (稀疏矩阵)")
    print("- company_patent_yearly.csv (CSV格式)")
    
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
    sparse_matrix, company_names, years = analyze_company_patents()
    
    # 演示查询功能
    print("\n" + "="*50)
    print("演示查询功能:")
    load_and_query_results()
    
    # 查询特定公司
    print("\n" + "="*50)
    print("查询特定公司专利:")
    query_company_patents("北京蓝晶微生物科技有限公司")
