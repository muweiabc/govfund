import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix

def quick_patent_check():
    """
    快速检查专利数据结构，测试小规模数据
    """
    print("=== 快速专利数据检查 ===")
    
    # 1. 检查filtered_companies
    print("\n1. 检查filtered_companies.csv:")
    try:
        companies_df = pd.read_csv('filtered_companies.csv')
        print(f"   - 文件行数: {len(companies_df)}")
        print(f"   - 列名: {list(companies_df.columns)}")
        print(f"   - 前3家公司: {companies_df['融资主体'].head(3).tolist()}")
    except Exception as e:
        print(f"   - 错误: {e}")
        return
    
    # 2. 检查trimpatent.csv（只读取前几行）
    print("\n2. 检查trimpatent.csv:")
    try:
        # 只读取前1000行来检查结构
        patents_sample = pd.read_csv('trimpatent.csv', nrows=1000)
        print(f"   - 样本行数: {len(patents_sample)}")
        print(f"   - 列名: {list(patents_sample.columns)}")
        print(f"   - 申请年份范围: {patents_sample['申请年份'].min()} - {patents_sample['申请年份'].max()}")
        
        # 检查申请人列的唯一值数量
        unique_applicants = patents_sample['申请人'].nunique()
        print(f"   - 样本中唯一申请人数量: {unique_applicants}")
        
        # 检查是否有匹配的公司
        sample_companies = set(companies_df['融资主体'].head(10).tolist())
        sample_applicants = set(patents_sample['申请人'].unique())
        matches = sample_companies.intersection(sample_applicants)
        print(f"   - 样本中匹配的公司数量: {len(matches)}")
        if matches:
            print(f"   - 匹配的公司: {list(matches)[:3]}")
        
    except Exception as e:
        print(f"   - 错误: {e}")
        return
    
    # 3. 测试小规模数据处理
    print("\n3. 测试小规模数据处理:")
    try:
        # 只处理前1000行专利数据
        test_patents = patents_sample.copy()
        
        # 数据预处理
        test_patents['申请年份'] = pd.to_numeric(test_patents['申请年份'], errors='coerce')
        test_patents = test_patents.dropna(subset=['申请年份'])
        test_patents['申请年份'] = test_patents['申请年份'].astype(int)
        
        # 获取年份范围
        years = sorted(test_patents['申请年份'].unique())
        print(f"   - 年份范围: {min(years)} - {max(years)}")
        
        # 统计每个公司在每年的专利数量
        company_patents = test_patents.groupby(['申请人', '申请年份']).size().reset_index(name='专利数量')
        print(f"   - 公司-年份组合数: {len(company_patents)}")
        
        # 显示一些示例
        print("\n   - 示例数据:")
        for _, row in company_patents.head(5).iterrows():
            print(f"     {row['申请人']} - {row['申请年份']}年: {row['专利数量']}件")
            
    except Exception as e:
        print(f"   - 错误: {e}")
        return
    
    print("\n=== 快速检查完成 ===")

def test_company_match():
    """
    测试公司名称匹配
    """
    print("\n=== 测试公司名称匹配 ===")
    
    try:
        # 读取前1000行专利数据
        patents_sample = pd.read_csv('trimpatent.csv', nrows=1000)
        
        # 读取公司列表
        companies_df = pd.read_csv('filtered_companies.csv')
        
        # 获取前20家公司
        test_companies = companies_df['融资主体'].head(20).tolist()
        
        print(f"测试公司数量: {len(test_companies)}")
        
        # 统计匹配情况
        matches = []
        for company in test_companies:
            count = len(patents_sample[patents_sample['申请人'] == company])
            if count > 0:
                matches.append((company, count))
        
        print(f"找到匹配的公司数量: {len(matches)}")
        
        if matches:
            print("\n匹配的公司及其专利数量:")
            for company, count in matches[:10]:  # 只显示前10个
                print(f"  {company}: {count}件专利")
        
        # 检查匹配率
        match_rate = len(matches) / len(test_companies) * 100
        print(f"\n匹配率: {match_rate:.1f}%")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")

def analyze_companies_without_patents():
    """
    分析没有专利的公司数量和占比
    读取company_patent_yearly.csv文件，统计完全没有专利的公司
    """
    try:
        # 读取专利年度数据
        df = pd.read_csv('company_patent_yearly.csv', index_col=0)
        
        # 计算每个公司的总专利数（所有年份的总和）
        total_patents = df.sum(axis=1)
        
        # 统计没有专利的公司
        companies_without_patents = total_patents[total_patents == 0]
        companies_with_patents = total_patents[total_patents > 0]
        
        # 计算数量和占比
        total_companies = len(df)
        no_patent_count = len(companies_without_patents)
        has_patent_count = len(companies_with_patents)
        
        no_patent_percentage = (no_patent_count / total_companies) * 100
        has_patent_percentage = (has_patent_count / total_companies) * 100
        
        print("=" * 60)
        print("公司专利情况分析报告")
        print("=" * 60)
        print(f"总公司数量: {total_companies:,}")
        print(f"有专利的公司数量: {has_patent_count:,}")
        print(f"没有专利的公司数量: {no_patent_count:,}")
        print("-" * 60)
        print(f"有专利的公司占比: {has_patent_percentage:.2f}%")
        print(f"没有专利的公司占比: {no_patent_percentage:.2f}%")
        print("=" * 60)
        
        # 显示一些没有专利的公司示例
        if no_patent_count > 0:
            print(f"\n没有专利的公司示例（前10个）:")
            for company in companies_without_patents.index[:10]:
                print(f"  - {company}")
            
            if no_patent_count > 10:
                print(f"  ... 还有 {no_patent_count - 10} 家公司")
        
        # 显示一些有专利的公司示例
        if has_patent_count > 0:
            print(f"\n有专利的公司示例（前10个）:")
            for company in companies_with_patents.index[:10]:
                patent_count = total_patents[company]
                print(f"  - {company}: {patent_count:,} 件专利")
            
            if has_patent_count > 10:
                print(f"  ... 还有 {has_patent_count - 10} 家公司")
        
        # 返回统计结果
        return {
            'total_companies': total_companies,
            'companies_with_patents': has_patent_count,
            'companies_without_patents': no_patent_count,
            'has_patent_percentage': has_patent_percentage,
            'no_patent_percentage': no_patent_percentage,
            'companies_without_patents_list': companies_without_patents.index.tolist()
        }
        
    except FileNotFoundError:
        print("错误: 找不到 company_patent_yearly.csv 文件")
        return None
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        return None




if __name__ == "__main__":
    # quick_patent_check()
    # test_company_match()
    result = analyze_companies_without_patents()
    
    if result:
        print(f"\n分析完成！")
        print(f"建议: 重点关注 {result['companies_without_patents']} 家没有专利的公司")


def export_companies_with_patents_to_excel():
    """
    将有专利的公司输出到company_patent_yearly.csv对应的Excel文件的新sheet中
    """
    try:
        print("=== 导出有专利的公司到Excel ===")
        
        # 读取专利年度数据
        print("1. 读取专利年度数据...")
        df = pd.read_csv('company_patent_yearly.csv', index_col=0)
        print(f"   - 总公司数量: {len(df):,}")
        
        # 计算每个公司的总专利数
        print("2. 计算公司专利总数...")
        total_patents = df.sum(axis=1)
        
        # 分离有专利和没有专利的公司
        companies_with_patents = total_patents[total_patents > 0]
        companies_without_patents = total_patents[total_patents == 0]
        
        print(f"   - 有专利的公司数量: {len(companies_with_patents):,}")
        print(f"   - 没有专利的公司数量: {len(companies_without_patents):,}")
        
        # 创建有专利公司的数据框
        print("3. 准备有专利公司的数据...")
        companies_with_patents_df = df.loc[companies_with_patents.index].copy()
        
        # 添加总专利数列
        companies_with_patents_df['总专利数'] = companies_with_patents
        
        # 按总专利数排序
        companies_with_patents_df = companies_with_patents_df.sort_values('总专利数', ascending=False)
        
        # 创建没有专利公司的数据框
        companies_without_patents_df = df.loc[companies_without_patents.index].copy()
        companies_without_patents_df['总专利数'] = 0
        
        # 尝试读取现有的Excel文件，如果不存在则创建新的
        excel_filename = 'company_patent_yearly.xlsx'
        
        try:
            print(f"4. 尝试读取现有Excel文件: {excel_filename}")
            with pd.ExcelWriter(excel_filename, engine='openpyxl', mode='a') as writer:
                # 写入有专利的公司到新sheet
                companies_with_patents_df.to_excel(writer, sheet_name='有专利公司', index=True)
                print(f"   - 成功添加'有专利公司'sheet，包含 {len(companies_with_patents_df)} 家公司")
                
                # 写入没有专利的公司到新sheet
                companies_without_patents_df.to_excel(writer, sheet_name='无专利公司', index=True)
                print(f"   - 成功添加'无专利公司'sheet，包含 {len(companies_without_patents_df)} 家公司")
                
        except FileNotFoundError:
            print(f"4. 创建新的Excel文件: {excel_filename}")
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                # 写入原始数据
                df.to_excel(writer, sheet_name='原始数据', index=True)
                
                # 写入有专利的公司
                companies_with_patents_df.to_excel(writer, sheet_name='有专利公司', index=True)
                print(f"   - 成功创建'有专利公司'sheet，包含 {len(companies_with_patents_df)} 家公司")
                
                # 写入没有专利的公司
                companies_without_patents_df.to_excel(writer, sheet_name='无专利公司', index=True)
                print(f"   - 成功创建'无专利公司'sheet，包含 {len(companies_without_patents_df)} 家公司")
        
        print(f"\n5. 导出完成！")
        print(f"   - Excel文件: {excel_filename}")
        print(f"   - 有专利公司: {len(companies_with_patents_df):,} 家")
        print(f"   - 无专利公司: {len(companies_without_patents_df):,} 家")
        
        # 显示一些统计信息
        print(f"\n6. 专利统计信息:")
        print(f"   - 专利最多的公司: {companies_with_patents_df.index[0]}")
        print(f"   - 专利数量: {companies_with_patents_df['总专利数'].iloc[0]:,}")
        print(f"   - 平均专利数: {companies_with_patents_df['总专利数'].mean():.1f}")
        print(f"   - 中位数专利数: {companies_with_patents_df['总专利数'].median():.1f}")
        
        return {
            'excel_file': excel_filename,
            'companies_with_patents': len(companies_with_patents_df),
            'companies_without_patents': len(companies_without_patents_df),
            'total_companies': len(df)
        }
        
    except FileNotFoundError:
        print("错误: 找不到 company_patent_yearly.csv 文件")
        return None
    except Exception as e:
        print(f"导出过程中出现错误: {str(e)}")
        return None

if __name__ == "__main__":
    # 运行专利分析并导出到Excel
    result = export_companies_with_patents_to_excel()
    
    if result:
        print(f"\n=== 导出成功 ===")
        print(f"建议查看Excel文件: {result['excel_file']}")
        print(f"重点关注 {result['companies_without_patents']} 家没有专利的公司")
