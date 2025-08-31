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

def describe_excel_columns(input_file: str, sheet_name: str = None, columns: List[str] = None, 
                          output_file: str = None, output_sheet: str = '描述性统计') -> pd.DataFrame:
    """
    读取Excel文件中的数据表，对指定列进行描述性统计，并将结果附加到Excel表中
    
    参数:
        input_file: 输入的Excel文件路径
        sheet_name: 要读取的工作表名称，如果为None则读取第一个工作表
        columns: 要进行描述性统计的列名列表，如果为None则对所有数值列进行统计
        output_file: 输出文件路径，如果为None则覆盖原文件
        output_sheet: 输出统计结果的工作表名称
        
    返回:
        包含描述性统计结果的DataFrame
    """
    try:
        print(f"正在读取Excel文件: {input_file}")
        
        # 读取Excel文件
        if sheet_name is None:
            # 如果没有指定工作表，读取第一个工作表
            df = pd.read_excel(input_file)
            sheet_name = df.name if hasattr(df, 'name') else 'Sheet1'
        else:
            df = pd.read_excel(input_file, sheet_name=sheet_name)
        
        print(f"成功读取工作表: {sheet_name}")
        print(f"数据形状: {df.shape}")
        
        # 如果没有指定列，则对所有数值列进行统计
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
            print(f"自动选择数值列: {columns}")
        else:
            # 检查指定的列是否存在
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                print(f"警告: 以下列不存在于数据中: {missing_cols}")
                columns = [col for col in columns if col in df.columns]
            
            if not columns:
                print("错误: 没有找到有效的列进行统计")
                return None
        
        print(f"将对以下列进行描述性统计: {columns}")
        
        # 对每列进行描述性统计
        stats_results = []
        for col in columns:
            if col in df.columns:
                col_data = df[col].dropna()  # 移除NaN值
                if len(col_data) > 0:
                    stats = describe_sequence(col_data)
                    stats['列名'] = col
                    stats_results.append(stats)
                else:
                    print(f"警告: 列 '{col}' 没有有效数据")
        
        if not stats_results:
            print("错误: 没有生成任何统计结果")
            return None
        
        # 创建统计结果DataFrame
        stats_df = pd.DataFrame(stats_results)
        
        # 重新排列列的顺序，使列名在最前面
        cols_order = ['列名'] + [col for col in stats_df.columns if col != '列名']
        stats_df = stats_df[cols_order]
        
        # 格式化数值列，保留4位小数
        numeric_cols = ['均值', '标准差', '最小值', '中位数', '最大值']
        for col in numeric_cols:
            if col in stats_df.columns:
                stats_df[col] = stats_df[col].round(4)
        
        print("\n描述性统计结果:")
        print("=" * 80)
        print(stats_df.to_string(index=False))
        print("=" * 80)
        
        # 保存结果到Excel文件
        output_path = output_file if output_file else input_file
        
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl', mode='a' if output_file == input_file else 'w') as writer:
                # 如果输出到新文件，先写入原数据
                if output_file != input_file:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 写入统计结果
                stats_df.to_excel(writer, sheet_name=output_sheet, index=False)
                
            print(f"✅ 统计结果已保存到: {output_path}")
            print(f"   - 原数据工作表: {sheet_name}")
            print(f"   - 统计结果工作表: {output_sheet}")
            
        except Exception as e:
            print(f"保存文件时出现错误: {e}")
            print("尝试创建新文件...")
            
            # 如果追加模式失败，创建新文件
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                stats_df.to_excel(writer, sheet_name=output_sheet, index=False)
            
            print(f"✅ 统计结果已保存到新文件: {output_path}")
        
        return stats_df
        
    except Exception as e:
        print(f"处理Excel文件时出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None

# 示例用法
if __name__ == "__main__":
    # 示例1: 对指定列进行描述性统计并保存到原文件
    print("=== 示例1: 对指定列进行描述性统计 ===")
    stats_result = describe_excel_columns(
        input_file='patent_analysis/did_panel_data_patents_with_year_dummies.xlsx',
        sheet_name='面板数据',
        # columns=['投资当年GDP', '前3年专利数_前1年', '后3年专利数_后1年'],
        output_sheet='GDP和专利统计'
    )
    
   