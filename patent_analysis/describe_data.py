import numpy as np
import pandas as pd
from typing import Union, List, Tuple

def describe_sequence(data: Union[List, np.ndarray, pd.Series]) -> dict:
    """
    计算数据序列的统计描述
    
    参数:
        data: 输入的数据序列，可以是列表、numpy数组或pandas Series
        
    返回:
        包含统计信息的字典
    """
    # 转换为numpy数组以便计算
    if isinstance(data, (list, tuple)):
        data = np.array(data)
    elif isinstance(data, pd.Series):
        data = data.values
    elif not isinstance(data, np.ndarray):
        raise TypeError("输入数据类型必须是列表、numpy数组或pandas Series")
    
    # 移除NaN值
    data_clean = data[~np.isnan(data)]
    
    if len(data_clean) == 0:
        return {
            "均值": np.nan,
            "标准差": np.nan,
            "最小值": np.nan,
            "中位数": np.nan,
            "最大值": np.nan,
            "观测数": 0
        }
    
    # 计算统计量
    stats = {
        "均值": float(np.mean(data_clean)),
        "标准差": float(np.std(data_clean, ddof=1)),  # 样本标准差
        "最小值": float(np.min(data_clean)),
        "中位数": float(np.median(data_clean)),
        "最大值": float(np.max(data_clean)),
        "观测数": int(len(data_clean))
    }
    
    return stats

def print_describe_sequence(data: Union[List, np.ndarray, pd.Series]) -> None:
    """
    打印数据序列的统计描述
    
    参数:
        data: 输入的数据序列
    """
    stats = describe_sequence(data)
    
    print("数据序列统计描述:")
    print("=" * 30)
    for key, value in stats.items():
        if key == "观测数":
            print(f"{key}: {value}")
        else:
            print(f"{key}: {value:.4f}")
    print("=" * 30)

# 示例用法
if __name__ == "__main__":
    df = pd.read_excel('regress_data_with_gdp.xlsx', sheet_name='回归数据') 
    patent_pre_1 = df['前3年专利数_前1年']
    patent_pre_2 = df['前3年专利数_前2年']
    patent_pre_3 = df['前3年专利数_前3年']
    patent_post_1 = df['后3年专利数_后1年']
    patent_post_2 = df['后3年专利数_后2年']
    patent_post_3 = df['后3年专利数_后3年']
    patent = pd.concat([patent_pre_1, patent_pre_2, patent_pre_3, patent_post_1, patent_post_2, patent_post_3], axis=1)
    print_describe_sequence(patent)