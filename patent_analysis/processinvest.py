import pandas as pd
import os
import glob

def read_and_merge_investment_data():
    """
    读取../政府引导基金投资事件 文件夹中2000及以后的文件，合并所有数据到invest.xlsx中
    """
    folder_path = "../政府引导基金投资事件"
    
    # 定义要处理的文件（2000年及以后）
    target_files = [
        "2000-2012.xls",
        "2013-2014.xls", 
        "2015.xls",
        "2016.xls",
        "2017.xls",
        "2018.xls",
        "2019.xls",
        "2020.xls",
        "2021.xls",
    ]
    
    all_data = []
    
    for filename in target_files:
        file_path = os.path.join(folder_path, filename)
        
        if os.path.exists(file_path):
            try:
                print(f"正在处理文件: {filename}")
                
                # 读取Excel文件，以第4行（索引为3）作为列名
                df = pd.read_excel(file_path, header=3)
                
                print(f"  - 数据形状: {df.shape}")
                print(f"  - 列名: {list(df.columns)}")
                
                # 添加文件来源标识
                df['数据来源文件'] = filename
                
                all_data.append(df)
                print(f"  - 成功读取 {len(df)} 行数据")
                
            except Exception as e:
                print(f"  - 处理文件 {filename} 时发生错误: {e}")
        else:
            print(f"文件不存在: {file_path}")
    
    if all_data:
        try:
            # 合并所有数据
            merged_df = pd.concat(all_data, ignore_index=True)
            
            print(f"\n=== 合并结果 ===")
            print(f"总行数: {len(merged_df)}")
            print(f"总列数: {len(merged_df.columns)}")
            print(f"列名: {list(merged_df.columns)}")
            
            # 查找时间相关列进行排序
            time_columns = [col for col in merged_df.columns if '时间' in str(col) or '日期' in str(col) or '年' in str(col)]
            print(f"找到的时间相关列: {time_columns}")
            
            if time_columns:
                # 按时间倒序排序
                merged_df = merged_df.sort_values(by=time_columns[0], ascending=False)
                print(f"已按 {time_columns[0]} 倒序排序")
            else:
                print("未找到时间列，按数据来源文件排序")
                merged_df = merged_df.sort_values(by='数据来源文件', ascending=False)
            
            # 保存到invest.xlsx
            output_filename = "invest.xlsx"
            merged_df.to_excel(output_filename, index=False, sheet_name='所有投资')
            
            print(f"\n数据已成功保存到 {output_filename}")
            print(f"文件大小: {os.path.getsize(output_filename) / (1024*1024):.2f} MB")
            
            filtered_companies = merged_df['融资主体'].value_counts()
            # 去掉不披露的融资主体
            with pd.ExcelWriter(output_filename, engine='openpyxl', mode='a') as writer:
                filtered_companies[1:,].to_excel(writer, sheet_name='去重公司列表',index=True)
            return merged_df
            
        except Exception as e:
            print(f"合并数据时发生错误: {e}")
            return None
    else:
        print("没有成功读取任何文件")
        return None
    

def add_treatment_column():
    """
    为invest.xlsx添加treatment列
    如果"基金名称"出现在govfund_filtered.xlsx中，该行的treatment值为1，否则为0
    """
    try:
        print("=== 添加treatment列 ===")
        
        # 1. 读取invest.xlsx文件
        print("1. 读取invest.xlsx文件...")
        invest_df = pd.read_excel('invest.xlsx', sheet_name='所有投资')
        print(f"   - 投资数据行数: {len(invest_df):,}")
        print(f"   - 列数: {len(invest_df.columns)}")
        
        # 2. 读取govfund_filtered.xlsx文件
        print("2. 读取govfund_filtered.xlsx文件...")
        govfund_df = pd.read_excel('govfund_filtered.xlsx')
        print(f"   - 政府基金数据行数: {len(govfund_df):,}")
        
        # 3. 创建政府基金名称集合（包括简称和全称）
        print("3. 创建政府基金名称集合...")
        govfund_names = set()
        
        # 添加基金简称
        if '基金简称' in govfund_df.columns:
            govfund_names.update(govfund_df['基金简称'].dropna().astype(str).tolist())
            print(f"   - 基金简称数量: {govfund_df['基金简称'].dropna().count()}")
        
        # 添加基金全称
        if '基金全称' in govfund_df.columns:
            govfund_names.update(govfund_df['基金全称'].dropna().astype(str).tolist())
            print(f"   - 基金全称数量: {govfund_df['基金全称'].dropna().count()}")
        
        print(f"   - 政府基金名称总数: {len(govfund_names):,}")
        
        # 4. 创建treatment列
        print("4. 创建treatment列...")
        invest_df['treatment'] = 0  # 默认值为0
        
        # 检查基金名称是否在政府基金名称集合中
        if '基金名称' in invest_df.columns:
            # 使用apply函数来检查每一行
            def check_treatment(fund_name):
                if pd.isna(fund_name) or fund_name == '':
                    return 0
                return 1 if str(fund_name) in govfund_names else 0
            
            invest_df['treatment'] = invest_df['基金名称'].apply(check_treatment)
            
            # 统计treatment的分布
            treatment_counts = invest_df['treatment'].value_counts()
            print(f"   - treatment=0 (非政府基金): {treatment_counts.get(0, 0):,}")
            print(f"   - treatment=1 (政府基金): {treatment_counts.get(1, 0):,}")
            
            # 计算匹配率
            match_rate = (treatment_counts.get(1, 0) / len(invest_df)) * 100
            print(f"   - 政府基金匹配率: {match_rate:.2f}%")
            
            # 显示一些匹配的示例
            matched_examples = invest_df[invest_df['treatment'] == 1]['基金名称'].head(5).tolist()
            if matched_examples:
                print(f"   - 匹配的政府基金示例:")
                for example in matched_examples:
                    print(f"     * {example}")
            
            # 显示一些未匹配的示例
            unmatched_examples = invest_df[invest_df['treatment'] == 0]['基金名称'].head(5).tolist()
            if unmatched_examples:
                print(f"   - 未匹配的基金示例:")
                for example in unmatched_examples:
                    print(f"     * {example}")
        else:
            print("错误: invest.xlsx中没有找到'基金名称'列")
            return None
        
        # 5. 保存更新后的文件
        print("5. 保存更新后的文件...")
        
        output_filename = 'invest.xlsx'
        with pd.ExcelWriter(output_filename, engine='openpyxl', mode='a') as writer:
            invest_df.to_excel(writer, sheet_name='treatment', index=False)
        
        print(f"   - 文件已保存为: {output_filename}")
        print(f"   - 文件大小: {os.path.getsize(output_filename) / (1024*1024):.2f} MB")
        
        # 6. 显示一些统计信息
        print("\n6. 统计信息:")
        print(f"   - 总投资事件: {len(invest_df):,}")
        print(f"   - 政府基金投资事件: {treatment_counts.get(1, 0):,}")
        print(f"   - 非政府基金投资事件: {treatment_counts.get(0, 0):,}")
        print(f"   - 政府基金占比: {match_rate:.2f}%")
        
        return {
            'total_investments': len(invest_df),
            'government_fund_investments': treatment_counts.get(1, 0),
            'non_government_fund_investments': treatment_counts.get(0, 0),
            'match_rate': match_rate,
            'output_file': output_filename
        }
        
    except FileNotFoundError as e:
        print(f"文件未找到错误: {e}")
        return None
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        return None

def extract_first_investment_for_patent_companies():
    """
    从company_patent_yearly.xlsx中读取有专利公司sheet，
    在invest中搜索每个公司获得的最早的一笔投资，
    把该行输出到invest的新sheet里
    """
    try:
        print("=== 提取有专利公司的首次投资记录 ===")
        
        # 1. 读取有专利公司数据
        print("1. 读取有专利公司数据...")
        try:
            patent_companies_df = pd.read_excel('company_patent_yearly.xlsx', sheet_name='有专利公司')
            print(f"   - 有专利公司数据形状: {patent_companies_df.shape}")
            
            # 检查公司名称列
            if 'Unnamed: 0' in patent_companies_df.columns:
                company_names = patent_companies_df['Unnamed: 0'].dropna().tolist()
                print(f"   - 有专利公司数量: {len(company_names):,}")
                print(f"   - 前5个公司名称: {company_names[:5]}")
            else:
                print("   错误: 找不到公司名称列")
                return None
                
        except Exception as e:
            print(f"   错误: 无法读取有专利公司sheet: {e}")
            return None
        
        # 2. 读取投资数据
        print("2. 读取投资数据...")
        invest_df = pd.read_excel('invest.xlsx', sheet_name='treatment')
        print(f"   - 投资记录总数: {len(invest_df):,}")
        
        # 3. 获取有专利的公司名称列表
        print("3. 获取有专利公司名称列表...")
        patent_companies = set(company_names)
        print(f"   - 有专利公司数量: {len(patent_companies):,}")
        
        # 4. 在投资数据中筛选有专利公司的记录
        print("4. 筛选有专利公司的投资记录...")
        patent_companies_investments = invest_df[invest_df['融资主体'].isin(patent_companies)]
        print(f"   - 有专利公司的投资记录数: {len(patent_companies_investments):,}")
        
        if len(patent_companies_investments) == 0:
            print("   警告: 没有找到匹配的投资记录，检查公司名称格式...")
            # 显示一些示例进行对比
            print("   有专利公司示例:")
            for i, company in enumerate(list(patent_companies)[:5]):
                print(f"     {i+1}. {company}")
            print("   投资数据融资主体示例:")
            for i, company in enumerate(invest_df['融资主体'].head(5).tolist()):
                print(f"     {i+1}. {company}")
            return None
        
        # 5. 处理投资时间，转换为日期格式
        print("5. 处理投资时间...")
        # 复制数据避免修改原始数据
        invest_filtered = patent_companies_investments.copy()
        
        # 转换投资时间为日期格式
        invest_filtered['投资时间_日期'] = pd.to_datetime(invest_filtered['投资时间'], errors='coerce')
        
        # 移除投资时间为空或无效的记录
        invest_filtered = invest_filtered.dropna(subset=['投资时间_日期'])
        print(f"   - 有效投资时间记录数: {len(invest_filtered):,}")
        
        # 6. 为每个公司找到最早的投资记录
        print("6. 查找每个公司的首次投资...")
        first_investments = []
        
        for company in patent_companies:
            company_investments = invest_filtered[invest_filtered['融资主体'] == company]
            
            if len(company_investments) > 0:
                # 找到最早的投资记录
                earliest_investment = company_investments.loc[company_investments['投资时间_日期'].idxmin()]
                first_investments.append(earliest_investment)
        
        print(f"   - 找到首次投资记录的公司数: {len(first_investments):,}")
        
        # 7. 创建首次投资数据框
        print("7. 创建首次投资数据框...")
        first_investments_df = pd.DataFrame(first_investments)
        
        # 移除临时的日期列
        if '投资时间_日期' in first_investments_df.columns:
            first_investments_df = first_investments_df.drop('投资时间_日期', axis=1)
        
        # 按投资时间排序
        first_investments_df['投资时间_排序'] = pd.to_datetime(first_investments_df['投资时间'], errors='coerce')
        first_investments_df = first_investments_df.sort_values('投资时间_排序')
        first_investments_df = first_investments_df.drop('投资时间_排序', axis=1)
        
        # 8. 保存到新的Excel文件
        print("8. 保存首次投资记录...")
        output_filename = 'invest.xlsx'
        
        try:
            # 尝试读取现有文件并添加新sheet
            with pd.ExcelWriter(output_filename, engine='openpyxl', mode='a') as writer:
                first_investments_df.to_excel(writer, sheet_name='有专利公司首次投资', index=False)
                print(f"   - 成功添加'有专利公司首次投资'sheet到 {output_filename}")
                
        except Exception as e:
            print(f"   警告: 无法追加到现有文件，创建新文件: {e}")
            # 如果无法追加，创建新文件
            first_investments_df.to_excel(output_filename, sheet_name='有专利公司首次投资', index=False)
            print(f"   - 创建新文件: {output_filename}")
        
        # 9. 显示统计信息
        print("\n9. 统计信息:")
        print(f"   - 有专利公司总数: {len(patent_companies):,}")
        print(f"   - 找到投资记录的公司数: {len(first_investments_df):,}")
        print(f"   - 未找到投资记录的公司数: {len(patent_companies) - len(first_investments_df):,}")
        
        # 显示一些示例
        if len(first_investments_df) > 0:
            print(f"\n10. 首次投资记录示例（前5个）:")
            for i, (_, row) in enumerate(first_investments_df.head().iterrows()):
                print(f"    {i+1}. {row['融资主体']} - {row['投资时间']} - {row['投资金额(RMB/M)']}M")
        
        # 10. 检查treatment分布
        if 'treatment' in first_investments_df.columns:
            treatment_counts = first_investments_df['treatment'].value_counts()
            print(f"\n11. Treatment分布:")
            print(f"    - treatment=0 (非政府基金): {treatment_counts.get(0, 0):,}")
            print(f"    - treatment=1 (政府基金): {treatment_counts.get(1, 0):,}")
            
            if len(first_investments_df) > 0:
                gov_fund_rate = (treatment_counts.get(1, 0) / len(first_investments_df)) * 100
                print(f"    - 政府基金首次投资占比: {gov_fund_rate:.2f}%")
        
        return {
            'total_patent_companies': len(patent_companies),
            'companies_with_investments': len(first_investments_df),
            'companies_without_investments': len(patent_companies) - len(first_investments_df),
            'output_file': output_filename,
            'first_investments_df': first_investments_df
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
    # 读取并合并投资事件数据
    read_and_merge_investment_data()
    # 添加treatment列

    result = add_treatment_column()
    
    # 提取有专利公司的首次投资记录
    
    result = extract_first_investment_for_patent_companies()
    
    # if result:
    #     print(f"\n=== 处理完成 ===")
    #     print(f"建议查看文件: {result['output_file']}")
    #     print(f"有专利公司总数: {result['total_patent_companies']:,}")
    #     print(f"找到首次投资记录的公司数: {result['companies_with_investments']:,}")
