import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
import traceback
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def read_govfund_data(file_path='govfund_filtered.xlsx'):
    """
    读取政府基金数据文件
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        pandas.DataFrame: 读取的数据
    """
    try:
        print(f"正在尝试读取文件: {file_path}")
        print(f"当前工作目录: {os.getcwd()}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: 文件不存在 - {file_path}")
            return None
            
        # 尝试读取Excel文件
        df = pd.read_excel(file_path)
        print(f"成功读取文件: {file_path}")
        print(f"数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        print("\n前5行数据:")
        print(df.head())
        print("\n数据类型:")
        print(df.dtypes)
        
        # 检查必要的列
        required_columns = ['成立时间', '注册地区']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"警告: 缺少必要的列: {missing_columns}")
            print(f"可用的列: {list(df.columns)}")
        
        return df
    except FileNotFoundError as e:
        print(f"文件未找到错误: {e}")
        print(f"请检查文件路径: {file_path}")
        return None
    except PermissionError as e:
        print(f"权限错误: {e}")
        print("请确保文件没有被其他程序占用")
        return None
    except Exception as e:
        print(f"读取文件时发生未知错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        print(f"详细错误信息:")
        traceback.print_exc()
        return None

def analyze_fund_establishment_by_year_province(df):
    """
    按年份和省份统计新成立的基金
    
    Args:
        df (pandas.DataFrame): 政府基金数据
        
    Returns:
        dict: 包含各种统计结果的字典
    """
    try:
        results = {}
        
        print("开始分析基金成立情况...")
        
        # 检查必要的列是否存在
        required_cols = ['成立时间', '注册地区']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"错误: 缺少必要的列: {missing_cols}")
            print(f"可用的列: {list(df.columns)}")
            return results
        
        # 使用第一个可用的日期列
        date_col = '成立时间'
        print(f"使用日期列: {date_col}")
        
        # 检查日期列的数据类型和内容
        print(f"日期列数据类型: {df[date_col].dtype}")
        print(f"日期列前5个值: {df[date_col].head().tolist()}")
        
        # 确保日期列是datetime类型
        if df[date_col].dtype != 'datetime64[ns]':
            print("正在转换日期列...")
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            print(f"转换后日期列数据类型: {df[date_col].dtype}")
            
            # 检查转换后的空值
            null_count = df[date_col].isnull().sum()
            if null_count > 0:
                print(f"警告: 日期转换后有 {null_count} 个空值")
        
        # 提取年份
        df['成立年份'] = df[date_col].dt.year
        print(f"年份列前5个值: {df['成立年份'].head().tolist()}")
        
        # 检查省份列
        province_col = '注册地区'
        print(f"使用省份列: {province_col}")
        print(f"省份列前5个值: {df[province_col].head().tolist()}")
        
        # 处理省份信息
        try:
            df['省份'] = df[province_col].apply(lambda x: x.split('|')[1] if '|' in str(x) else str(x))
            print("省份信息处理完成")
        except Exception as e:
            print(f"处理省份信息时出错: {e}")
            print("使用原始省份列")
            df['省份'] = df[province_col]
        
        # 检查处理后的数据
        print(f"处理后的省份列前5个值: {df['省份'].head().tolist()}")
        
        # 按年份和省份统计
        print("正在按年份和省份统计...")
        yearly_province_stats = df.groupby(['成立年份', '省份']).size().reset_index(name='基金数量')
        
        # 按年份统计总数
        yearly_stats = df.groupby('成立年份').size().reset_index(name='基金总数')
        
        # 按省份统计总数
        province_stats = df.groupby('省份').size().reset_index(name='基金总数')
        
        # 按年份和省份的透视表
        pivot_table = df.pivot_table(
            index='成立年份', 
            columns='省份', 
            values=df.columns[0],  # 使用第一列作为计数
            aggfunc='count',
            fill_value=0
        )
        
        results = {
            'yearly_province_stats': yearly_province_stats,
            'yearly_stats': yearly_stats,
            'province_stats': province_stats,
            'pivot_table': pivot_table,
            'date_column': date_col,
            'province_column': '省份'
        }
        
        print("\n=== 按年份和省份统计结果 ===")
        print("\n年份-省份统计:")
        print(yearly_province_stats)
        
        print("\n按年份统计:")
        print(yearly_stats)
        
        print("\n按省份统计:")
        print(province_stats)
        
        print("\n年份-省份透视表:")
        print(pivot_table)
        
        return results
        
    except Exception as e:
        print(f"分析过程中发生错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        print("详细错误信息:")
        traceback.print_exc()
        return {}

def visualize_results(results):
    """
    可视化统计结果
    
    Args:
        results (dict): 分析结果字典
    """
    if not results:
        print("没有结果可以可视化")
        return
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('政府基金成立情况分析', fontsize=16)
    
    # 1. 按年份趋势
    if 'yearly_stats' in results:
        ax1 = axes[0, 0]
        yearly_data = results['yearly_stats']
        ax1.plot(yearly_data['成立年份'], yearly_data['基金总数'], marker='o', linewidth=2, markersize=8)
        ax1.set_title('基金成立数量年度趋势')
        ax1.set_xlabel('年份')
        ax1.set_ylabel('基金数量')
        ax1.grid(True, alpha=0.3)
        
        # 添加数值标签
        for x, y in zip(yearly_data['成立年份'], yearly_data['基金总数']):
            ax1.annotate(str(y), (x, y), textcoords="offset points", xytext=(0,10), ha='center')
    
    # 2. 按省份分布
    if 'province_stats' in results:
        ax2 = axes[0, 1]
        province_data = results['province_stats']
        # 只显示前10个省份
        top_provinces = province_data.nlargest(10, '基金总数')
        ax2.barh(range(len(top_provinces)), top_provinces['基金总数'])
        ax2.set_yticks(range(len(top_provinces)))
        ax2.set_yticklabels(top_provinces[top_provinces.columns[0]])
        ax2.set_title('各省份基金数量分布 (前10名)')
        ax2.set_xlabel('基金数量')
        
        # 添加数值标签
        for i, v in enumerate(top_provinces['基金总数']):
            ax2.text(v, i, str(v), va='center')
    
    # 3. 热力图
    if 'pivot_table' in results:
        ax3 = axes[1, 0]
        pivot_data = results['pivot_table']
        # 只显示前10个省份
        if len(pivot_data.columns) > 10:
            pivot_data = pivot_data.iloc[:, :10]
        
        sns.heatmap(pivot_data, annot=True, fmt='d', cmap='YlOrRd', ax=ax3)
        ax3.set_title('年份-省份基金数量热力图')
        ax3.set_xlabel('省份')
        ax3.set_ylabel('年份')
    
    # 4. 按年份和省份的堆叠柱状图
    if 'yearly_province_stats' in results:
        ax4 = axes[1, 1]
        yearly_province_data = results['yearly_province_stats']
        # 获取前5个省份
        top_provinces = yearly_province_data.groupby(yearly_province_data.columns[1])['基金数量'].sum().nlargest(5).index
        
        # 为每个省份创建数据
        for province in top_provinces:
            province_data = yearly_province_data[yearly_province_data.iloc[:, 1] == province]
            ax4.plot(province_data.iloc[:, 0], province_data.iloc[:, 2], marker='s', label=province, linewidth=2)
        
        ax4.set_title('主要省份基金成立趋势')
        ax4.set_xlabel('年份')
        ax4.set_ylabel('基金数量')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def save_results_to_excel(results, output_file='govfund_analysis_results.xlsx'):
    """
    将分析结果保存到Excel文件
    
    Args:
        results (dict): 分析结果字典
        output_file (str): 输出文件名
    """
    if not results:
        print("没有结果可以保存")
        return
    
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            if 'yearly_province_stats' in results:
                results['yearly_province_stats'].to_excel(writer, sheet_name='年份省份统计', index=False)
            
            if 'yearly_stats' in results:
                results['yearly_stats'].to_excel(writer, sheet_name='年度统计', index=False)
            
            if 'province_stats' in results:
                results['province_stats'].to_excel(writer, sheet_name='省份统计', index=False)
            
            if 'pivot_table' in results:
                results['pivot_table'].to_excel(writer, sheet_name='年份省份透视表')
        
        print(f"分析结果已保存到: {output_file}")
    except Exception as e:
        print(f"保存文件时出错: {e}")

def main():
    """
    主函数
    """
    print("=== 政府基金数据分析 ===")
    print("正在读取数据文件...")
    
    # 读取数据
    df = read_govfund_data()
    
    if df is not None:
        print("\n开始分析数据...")
        
        # 分析数据
        results = analyze_fund_establishment_by_year_province(df)
        
        if results:
            print("\n开始生成可视化图表...")
            
            # 生成可视化
            visualize_results(results)
            
            # 保存结果
            save_results_to_excel(results)
            
            print("\n分析完成！")
        else:
            print("分析失败，请检查数据格式")
    else:
        print("无法读取数据文件")

if __name__ == "__main__":
    main()
