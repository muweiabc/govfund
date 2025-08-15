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
        "2022.xls",
        "2023.xls"
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
            merged_df.to_excel(output_filename, index=False)
            
            print(f"\n数据已成功保存到 {output_filename}")
            print(f"文件大小: {os.path.getsize(output_filename) / (1024*1024):.2f} MB")
            
            return merged_df
            
        except Exception as e:
            print(f"合并数据时发生错误: {e}")
            return None
    else:
        print("没有成功读取任何文件")
        return None

def filter_company(df):
    companies = pd.read_excel('invest.xlsx')
    filtered_companies = companies['融资主体'].value_counts()   
    filtered_companies[1:].to_csv('filtered_companies.csv')

def add_treatment_column():
    """
    为invest.xlsx添加treatment列
    如果"基金名称"出现在govfund_filtered.xlsx中，该行的treatment值为1，否则为0
    """
    try:
        print("=== 添加treatment列 ===")
        
        # 1. 读取invest.xlsx文件
        print("1. 读取invest.xlsx文件...")
        invest_df = pd.read_excel('invest.xlsx')
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
        output_filename = 'invest_with_treatment.xlsx'
        invest_df.to_excel(output_filename, index=False)
        
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

if __name__ == "__main__":
    # 读取并合并投资事件数据
    # merged_data = filter_company()
    # 添加treatment列
    result = add_treatment_column()
    
    if result:
        print(f"\n=== 处理完成 ===")
        print(f"建议查看文件: {result['output_file']}")
        print(f"政府基金投资事件占比: {result['match_rate']:.2f}%")
