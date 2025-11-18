#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析有专利公司首次投资的省份分布
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import traceback

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def analyze_province_distribution(file_path='invest.xlsx', sheet_name='有专利公司首次投资'):
    """
    分析有专利公司首次投资的省份分布
    
    Parameters:
    -----------
    file_path : str
        Excel文件路径
    sheet_name : str
        工作表名称
    
    Returns:
    --------
    dict : 各省份投资数量统计
    """
    
    # 读取数据
    print("正在读取数据...")
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(f"数据形状: {df.shape}")
    print(f"列名: {df.columns.tolist()}")
    
    # 检查'省份'列
    if '省份' not in df.columns:
        print("错误：未找到'省份'列")
        return None
    
    # 统计各省份数量
    province_counts = df['省份'].value_counts()
    print(f"\n各省份投资数量统计:")
    print(province_counts)
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('有专利公司首次投资 - 各省份数量分布', fontsize=16, fontweight='bold')
    
    # 1. 柱状图 - 前20个省份
    ax1 = axes[0, 0]
    top_20 = province_counts.head(20)
    bars = ax1.bar(range(len(top_20)), top_20.values, color='skyblue', alpha=0.7)
    ax1.set_title('前20个省份投资数量分布', fontsize=12, fontweight='bold')
    ax1.set_xlabel('省份')
    ax1.set_ylabel('投资数量')
    ax1.set_xticks(range(len(top_20)))
    ax1.set_xticklabels(top_20.index, rotation=45, ha='right')
    
    # 在柱子上添加数值标签
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom', fontsize=8)
    
    # 2. 饼图 - 前10个省份
    ax2 = axes[0, 1]
    top_10 = province_counts.head(10)
    others_count = province_counts.iloc[10:].sum()
    if others_count > 0:
        pie_data = list(top_10.values) + [others_count]
        pie_labels = list(top_10.index) + ['其他']
    else:
        pie_data = list(top_10.values)
        pie_labels = list(top_10.index)
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(pie_data)))
    wedges, texts, autotexts = ax2.pie(pie_data, labels=pie_labels, autopct='%1.1f%%', 
                                      colors=colors, startangle=90)
    ax2.set_title('前10个省份投资占比', fontsize=12, fontweight='bold')
    
    # 3. 水平柱状图 - 所有省份
    ax3 = axes[1, 0]
    y_pos = np.arange(len(province_counts))
    bars = ax3.barh(y_pos, province_counts.values, color='lightcoral', alpha=0.7)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(province_counts.index)
    ax3.set_xlabel('投资数量')
    ax3.set_title('所有省份投资数量分布', fontsize=12, fontweight='bold')
    ax3.invert_yaxis()  # 最高的在顶部
    
    # 4. 累积分布图
    ax4 = axes[1, 1]
    cumulative_counts = province_counts.cumsum()
    cumulative_pct = cumulative_counts / province_counts.sum() * 100
    ax4.plot(range(1, len(cumulative_pct) + 1), cumulative_pct.values, 
             marker='o', linewidth=2, markersize=4)
    ax4.set_xlabel('省份排名')
    ax4.set_ylabel('累积占比 (%)')
    ax4.set_title('投资数量累积分布', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 添加80%和90%的参考线
    ax4.axhline(y=80, color='red', linestyle='--', alpha=0.7, label='80%')
    ax4.axhline(y=90, color='orange', linestyle='--', alpha=0.7, label='90%')
    ax4.legend()
    
    plt.tight_layout()
    plt.show()
    
    # 输出统计信息
    print(f"\n统计摘要:")
    print(f"总省份数: {len(province_counts)}")
    print(f"总投资数: {province_counts.sum()}")
    print(f"平均每省投资数: {province_counts.mean():.2f}")
    print(f"投资数最多的省份: {province_counts.index[0]} ({province_counts.iloc[0]}次)")
    print(f"投资数最少的省份: {province_counts.index[-1]} ({province_counts.iloc[-1]}次)")
    
    # 计算集中度指标
    top_5_pct = province_counts.head(5).sum() / province_counts.sum() * 100
    top_10_pct = province_counts.head(10).sum() / province_counts.sum() * 100
    print(f"前5个省份占比: {top_5_pct:.1f}%")
    print(f"前10个省份占比: {top_10_pct:.1f}%")
    
    return province_counts.to_dict()

def draw_govfund_investment_piechart():
    """
    绘制政府基金投资事件的省份分布饼图
    """
    print("=== 绘制政府基金投资事件省份分布饼图 ===")
    
    try:
        # 读取投资数据
        df = pd.read_csv('invest_by_govfund.csv')
        print(f"成功读取投资数据，共 {len(df)} 条记录")
        
        df['省份'] = df['地区'].apply(lambda x: x.split('|')[1] if '|' in str(x) else str(x))
        # 处理省份数据
        df['省份'] = df['省份'].fillna('未知')
        df['省份'] = df['省份'].astype(str)
        
        # 统计各省份投资事件数量
        province_counts = df['省份'].value_counts()
        print(f"\n省份投资事件统计:")
        print(province_counts.head(10))
        
        # 创建饼图
        plt.figure(figsize=(12, 10))
        
        # 只显示前10个省份，其余合并为"其他"
        top_provinces = province_counts.head(10)
        other_count = province_counts.iloc[10:].sum() if len(province_counts) > 10 else 0
        
        # 准备饼图数据
        if other_count > 0:
            pie_data = list(top_provinces.values) + [other_count]
            pie_labels = list(top_provinces.index) + ['其他']
        else:
            pie_data = list(top_provinces.values)
            pie_labels = list(top_provinces.index)
        
        # 设置颜色
        colors = plt.cm.Set3(np.linspace(0, 1, len(pie_data)))
        
        # 绘制饼图
        wedges, texts, autotexts = plt.pie(pie_data, 
                                          labels=pie_labels,
                                          autopct='%1.1f%%',
                                          colors=colors,
                                          startangle=90,
                                          )  # 稍微分离每个扇形
        
        plt.title('政府基金投资事件省份分布', fontsize=16, fontweight='bold', pad=20)
        
        # 调整标签样式
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        # 添加图例，显示具体数量
        legend_labels = [f'{label}: {value:,}个' for label, value in zip(pie_labels, pie_data)]
        plt.legend(wedges, legend_labels, 
                  title="省份投资事件统计", 
                  loc="center left", 
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        # 确保图形是圆形
        plt.axis('equal')
        
        # 保存图片
        plt.tight_layout()
        plt.savefig('patent_analysis/graph/govfund_investment_province_pie.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 打印详细统计信息
        print(f"\n=== 省份投资事件详细统计 ===")
        print(f"总投资事件数: {len(df):,}")
        print(f"涉及省份数: {len(province_counts)}")
        print(f"\n前10个省份:")
        for i, (province, count) in enumerate(top_provinces.items(), 1):
            percentage = count / len(df) * 100
            print(f"{i:2d}. {province}: {count:,}个 ({percentage:.1f}%)")
        
        if other_count > 0:
            other_percentage = other_count / len(df) * 100
            print(f"    其他: {other_count:,}个 ({other_percentage:.1f}%)")
        
        return province_counts
        
    except FileNotFoundError:
        print("错误: 找不到文件 'invest_by_govfund.csv'")
        print("请确保文件存在或检查文件路径")
        return None
    except Exception as e:
        print(f"绘制饼图时发生错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        traceback.print_exc()
        return None


def main():
    """主函数"""
    try:
        # 分析省份分布
        province_stats = analyze_province_distribution()
        
        if province_stats:
            print("\n分析完成！")
        else:
            print("分析失败！")
            
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
  

if __name__ == "__main__":
    draw_govfund_investment_piechart()
