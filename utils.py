import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def winsorize_df(df, lower=0.01, upper=0.99):
    """
    对 DataFrame 中所有数值列进行缩尾处理（Winsorization）
    :param df: 输入 DataFrame
    :param lower: 下分位数，例如 0.01 表示保留下 1%
    :param upper: 上分位数，例如 0.99 表示保留上 99%
    :return: 缩尾后的 DataFrame 副本
    """
    df_winsor = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        low = df[col].quantile(lower)
        high = df[col].quantile(upper)
        df_winsor[col] = np.clip(df[col], low, high)
    
    return df_winsor


def read_finconstraints():
    """
    读取 finconstraints 数据文件
    使用空格作为分隔符，第一行是数据不是列名
    """
    file = 'finconstraints.csv'
    # 使用空格作为分隔符，第一行是数据不是列名
    df = pd.read_csv(file, delim_whitespace=True, header=None)
    
    # 将第二列的百分号数据转换为浮点数
    if len(df.columns) >= 2:
        # 使用列索引1访问第二列（因为header=None，列名是数字）
        col_idx = 1
        # 如果第二列是字符串类型且包含百分号，则转换
        if df[col_idx].dtype == 'object':
            # 去掉百分号并转换为浮点数
            df[col_idx] = df[col_idx].str.replace('%', '').astype(float) / 100
        elif df[col_idx].dtype in ['int64', 'float64']:
            # 如果已经是数值类型，假设是百分比形式（如50表示50%），转换为小数
            df[col_idx] = df[col_idx] / 100
    df.sort_values(by=1, ascending=True, inplace=True)
    return df

def analyze_finconstraints():
    """
    对 finconstraints 数据进行全面分析
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    print("=== finconstraints 数据分析 ===")
    
    # 读取数据
    df = read_finconstraints()
    
    print(f"\n数据基本信息:")
    print(f"数据形状: {df.shape}")
    print(f"列数: {len(df.columns)}")
    print(f"行数: {len(df)}")
    
    # 显示前几行数据
    print(f"\n前10行数据:")
    print(df.head(10))
    
    # 基本统计信息
    print(f"\n基本统计信息:")
    print(df.describe())
    
    # 如果有多列，分析各列的关系
    if len(df.columns) >= 2:
        print(f"\n列间相关性分析:")
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            print(corr_matrix)
        
        # 绘制散点图
        if len(df.columns) >= 2:
            plt.figure(figsize=(10, 6))
            plt.scatter(df[0], df[1], alpha=0.5)
            plt.xlabel('第一列')
            plt.ylabel('第二列')
            plt.title('finconstraints 数据散点图')
            plt.grid(True, alpha=0.3)
            plt.savefig('patent_analysis/graph/finconstraints_scatter.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        # 绘制第二列的分布直方图
        if df[1].dtype in ['int64', 'float64']:
            plt.figure(figsize=(10, 6))
            plt.hist(df[1], bins=30, edgecolor='black', alpha=0.7)
            plt.xlabel('第二列数值')
            plt.ylabel('频数')
            plt.title('finconstraints 第二列分布直方图')
            plt.grid(True, alpha=0.3)
            plt.savefig('patent_analysis/graph/finconstraints_hist.png', dpi=300, bbox_inches='tight')
            plt.show()
    
    # 保存分析结果到Excel
    output_file = 'patent_analysis/finconstraints_analysis.xlsx'
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 保存原始数据
        df.to_excel(writer, sheet_name='原始数据', index=False)
        
        # 保存描述性统计
        df.describe().to_excel(writer, sheet_name='描述性统计')
        
        # 如果有数值列，保存相关性矩阵
        if len(df.columns) >= 2:
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) > 1:
                numeric_df.corr().to_excel(writer, sheet_name='相关性矩阵')
    
    print(f"\n分析结果已保存到: {output_file}")
    
    return df

  