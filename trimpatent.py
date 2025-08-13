import pandas as pd
import os

# 按年份顺序定义文件列表
years = [2020, 2021, 2022, 2023, 2024, 2025]
data_dir = 'data'

# 存储所有数据框的列表
all_dfs = []

# 按年份顺序读取数据
for year in years:
    filename = f'中国专利数据库{year}年.csv'
    filepath = os.path.join(data_dir, filename)
    
    if os.path.exists(filepath):
        print(f'正在读取 {filename}...')
        try:
            # 读取指定列
            df = pd.read_csv(filepath, usecols=['专利类型','申请人','申请年份','公开公告年份','被引证次数'])
            print(f'{filename} 读取完成，共 {len(df)} 条记录')
            all_dfs.append(df)
        except Exception as e:
            print(f'读取 {filename} 时出错: {e}')
    else:
        print(f'文件 {filename} 不存在')

# 拼接所有数据
if all_dfs:
    print('正在拼接数据...')
    combined_df = pd.concat(all_dfs, ignore_index=True)
    print(f'数据拼接完成，总共 {len(combined_df)} 条记录')
    
    # 保存到trimpatent.csv
    output_file = 'trimpatent.csv'
    print(f'正在保存到 {output_file}...')
    combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f'数据已保存到 {output_file}')
    
    # 显示数据基本信息
    print('\n数据概览:')
    print(f'总记录数: {len(combined_df)}')
    print(f'列数: {len(combined_df.columns)}')
    print('\n列信息:')
    print(combined_df.info())
    print('\n前5行数据:')
    print(combined_df.head())
else:
    print('没有成功读取任何数据文件')

                 
