import pandas as pd

def read_govfund_data():
    """
    读取govfund1.xls文件的数据并存入DataFrame
    以第4行作为列名，出资人名称列类型为list
    """
    try:
        # 读取Excel文件，以第4行（索引为3）作为列名
        df = pd.read_excel('govfund1.xls', header=3)
        
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

if __name__ == "__main__":
    # 读取数据
    govfund_df = read_govfund_data()
    
    # 分析数据
    analyze_data(govfund_df)


