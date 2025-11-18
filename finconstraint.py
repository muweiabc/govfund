import pandas as pd
import numpy as np

def analyze_finconstraints():
    """
    读取 finconstraints.xlsx，去掉 FC、KZ、SA、WW 为空的行，
    按行业代码分组，计算 FC、KZ、SA、WW 的平均值，保留行业代码和行业名称
    """
    # 读取数据
    df = pd.read_excel('finconstraint.xlsx')
    
    print("=== finconstraints 数据分析 ===")
    print(f"原始数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    print(f"\n前5行数据:")
    print(df.head())
    
    # 检查必要的列是否存在
    required_cols = ['FC', 'KZ', 'SA', 'WW', '行业代码', '行业名称']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"错误: 缺少必要的列: {missing_cols}")
        print(f"可用的列: {list(df.columns)}")
        return None
    
    # 去掉 FC、KZ、SA、WW 为空的行
    print(f"\n去掉空值前的行数: {len(df)}")
    
    # 去掉这四个列中任意一个为空的行
    df_cleaned = df.dropna(subset=['FC', 'KZ', 'SA', 'WW'])
    
    print(f"去掉空值后的行数: {len(df_cleaned)}")
    print(f"删除了 {len(df) - len(df_cleaned)} 行空值数据")
    
    # 按行业代码分组，计算平均值
    print(f"\n按行业代码分组统计...")
    
    # 先获取每个行业代码对应的行业名称（取第一个，因为同一行业代码应该有相同的行业名称）
    industry_info = df_cleaned.groupby('行业代码').agg({
        '行业名称': 'first'  # 取第一个行业名称
    }).reset_index()
    
    # 计算各指标的平均值
    industry_stats = df_cleaned.groupby('行业代码').agg({
        'FC': 'mean',
        'KZ': 'mean',
        'SA': 'mean',
        'WW': 'mean'
    }).reset_index()
    
    # 合并行业名称
    result = industry_info.merge(industry_stats, on='行业代码', how='inner')
    
    # 重命名列，添加"平均值"后缀
    result = result.rename(columns={
        'FC': 'FC平均值',
        'KZ': 'KZ平均值',
        'SA': 'SA平均值',
        'WW': 'WW平均值'
    })
    
    # 重新排列列的顺序：行业代码、行业名称、FC平均值、KZ平均值、SA平均值、WW平均值
    result = result[['行业代码', '行业名称', 'FC平均值', 'KZ平均值', 'SA平均值', 'WW平均值']]
    
    print(f"\n分组统计结果:")
    print(f"行业数量: {len(result)}")
    print(f"\n前10行结果:")
    print(result.head(10))

    # 保存结果
    output_file = 'finconstraints_analysis.csv'
    result.to_csv(output_file, index=False)
    # with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    #     # 保存清理后的原始数据
    #     df_cleaned.to_excel(writer, sheet_name='清理后原始数据', index=False)
        
    #     # 保存按行业分组的平均值
    #     result.to_excel(writer, sheet_name='行业平均值', index=False)
        
    #     # 保存描述性统计
    #     result.describe().to_excel(writer, sheet_name='描述性统计')
    
    print(f"\n分析结果已保存到: {output_file}")
    
    # 显示统计摘要
    print(f"\n=== 统计摘要 ===")
    print(f"FC平均值范围: {result['FC平均值'].min():.4f} - {result['FC平均值'].max():.4f}")
    print(f"KZ平均值范围: {result['KZ平均值'].min():.4f} - {result['KZ平均值'].max():.4f}")
    print(f"SA平均值范围: {result['SA平均值'].min():.4f} - {result['SA平均值'].max():.4f}")
    print(f"WW平均值范围: {result['WW平均值'].min():.4f} - {result['WW平均值'].max():.4f}")
    
    return result

def get_industry():
    df = pd.read_excel('invest.xlsx',sheet_name='有专利公司首次投资')
    df['一级行业'] = df['行业(国标)'].apply(lambda x: x.split('|')[0])
    df['二级行业'] = df['行业(国标)'].apply(lambda x: x.split('|')[1] if len(x.split('|')) > 1 else None)
    
    constraint_df = pd.read_csv('finconstraints_analysis.csv')
    constraint_df['行业名称'] = constraint_df['行业名称'].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # 按二级行业与行业名称匹配，合并FC/KZ/SA/WW平均值
    merged_df = df.merge(
        constraint_df[['行业名称', 'FC平均值', 'KZ平均值', 'SA平均值', 'WW平均值']].rename(columns={'行业名称': '二级行业'}),
        on='二级行业',
        how='left'
    )
    merged_df = merged_df.dropna(subset=['FC平均值'])
    merged_df.sort_values(by=['FC平均值'], inplace=True)
    merged_df['group'] =  pd.qcut(
        merged_df['FC平均值'],
        q=2,
        labels=['a','b']
    )
    with pd.ExcelWriter('invest_industry.xlsx', engine='openpyxl') as writer:
        merged_df.to_excel(writer, sheet_name='行业分组', index=False)
    
if __name__ == "__main__":
    # result = analyze_finconstraints()
    get_industry()