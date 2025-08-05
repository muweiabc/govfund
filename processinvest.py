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

if __name__ == "__main__":
    # 读取并合并投资事件数据
    merged_data = read_and_merge_investment_data()
