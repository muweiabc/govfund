import pandas as pd

def read_govfund_data():
    """
    读取govfund1.xls文件的数据并存入DataFrame
    以第4行作为列名，出资人名称列类型为list
    """
    try:
        # 读取Excel文件，以第4行（索引为3）作为列名
        df = pd.read_excel('govfund1.xlsx', header=3)
        
        print("数据读取成功！")
        print(f"数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        print("\n前5行数据:")
        print(df.head(10))
        
        # 处理出资人名称列，将其转换为list类型
        if '出资人名称' in df.columns:
            # 将出资人名称列转换为字符串，然后按分隔符分割成list
            df['出资人名称'] = df['出资人名称'].astype(str).apply(
                lambda x: x.split(',') if ',' in x else [x] if x != 'nan' else []
            )
            print("\n出资人名称列已转换为list类型")
        
        return df
    
    except FileNotFoundError:
        print("错误: 找不到govfund1.xls文件")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None

def analyze_data(df):
    """
    分析数据的基本信息
    """
    if df is not None:
        print("\n=== 数据基本信息 ===")
        print(f"数据行数: {len(df)}")
        print(f"数据列数: {len(df.columns)}")
        print("\n数据类型:")
        print(df.dtypes)
        print("\n缺失值统计:")
        print(df.isnull().sum())
        
        # 检查出资人名称列
        if '出资人名称' in df.columns:
            print("\n出资人名称列示例:")
            print(df['出资人名称'].head())
            print(f"出资人名称列类型: {type(df['出资人名称'].iloc[0])}")
        
        print("\n数据描述性统计:")
        print(df.describe())

def filter_and_save_data(df):
    """
    依次处理政府引导基金123，结果合并保存在govfund_filtered中
    """
    files_to_process = [
        ('政府引导基金1.xlsx', '政府引导基金1'),
        ('政府引导基金2.xlsx', '政府引导基金2'),
        ('政府引导基金3.xlsx', '政府引导基金3')
    ]
    
    all_filtered_data = []
    
    for filename, fund_name in files_to_process:
        try:
            print(f"\n=== 处理{fund_name} ===")
            
            # 读取Excel文件，以第4行（索引为3）作为列名
            df = pd.read_excel(filename, header=3)
            print(f"{fund_name}数据读取成功！")
            print(f"数据形状: {df.shape}")
            print(f"列名: {list(df.columns)}")
            
            # 处理出资人名称列，将其转换为list类型
            if '出资人名称' in df.columns:
                df['出资人名称'] = df['出资人名称'].astype(str).apply(
                    lambda x: x.split(',') if ',' in x else [x] if x != 'nan' else []
                )
                print(f"{fund_name}出资人名称列已转换为list类型")
            
            # 获取第一列的名称
            first_column = df.columns[0]
            print(f"第一列名称: {first_column}")
            
            # 过滤出第一列非NaN的行
            filtered_df = df.dropna(subset=[first_column])
            print(f"过滤前行数: {len(df)}")
            print(f"过滤后行数: {len(filtered_df)}")
            
            # 排除"出资人名称"列
            if '出资人名称' in filtered_df.columns:
                filtered_df = filtered_df.drop(columns=['出资人名称'])
                print("已排除'出资人名称'列")
            
            print(f"最终列数: {len(filtered_df.columns)}")
            
            # 添加来源标识列
            filtered_df['数据来源'] = fund_name
            
            all_filtered_data.append(filtered_df)
            print(f"{fund_name}处理完成")
            
        except FileNotFoundError:
            print(f"错误: 找不到{filename}文件")
        except Exception as e:
            print(f"处理{fund_name}时发生错误: {e}")
    
    # 合并所有过滤后的数据
    if all_filtered_data:
        try:
            combined_df = pd.concat(all_filtered_data, ignore_index=True)
            print(f"\n合并后总行数: {len(combined_df)}")
            print(f"合并后总列数: {len(combined_df.columns)}")
            
            # 保存合并后的数据到govfund_filtered.xlsx
            output_filename = 'govfund_filtered.xlsx'
            combined_df.to_excel(output_filename, sheet_name='合并数据', index=False)
            print(f"数据已成功保存到'{output_filename}'文件的'合并数据'sheet中")
            
            return combined_df
                
        except Exception as e:
            print(f"合并数据时发生错误: {e}")
            return None
    else:
        print("没有成功处理任何文件")
        return None



if __name__ == "__main__":
    # 过滤并保存数据（处理所有三个政府引导基金文件）
    filtered_data = filter_and_save_data(None)


