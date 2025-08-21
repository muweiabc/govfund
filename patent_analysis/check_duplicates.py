import pandas as pd

# 读取数据
invest_df = pd.read_excel('invest.xlsx')
fund_df = pd.read_excel('govfund_filtered.xlsx')

print("=== 检查fund_df中简称重复的情况 ===")
print(f"fund_df数据形状: {fund_df.shape}")
print(f"fund_df列名: {list(fund_df.columns)}")

# 查找基金简称列
fund_name_col = None
for col in fund_df.columns:
    if '基金简称' in str(col) or '基金名称' in str(col):
        fund_name_col = col
        break

if fund_name_col is None:
    print("错误: 未找到基金简称列")
    print("可用列名:", list(fund_df.columns))
else:
    print(f"使用列名: {fund_name_col}")
    
    # 检查重复值
    fund_names = fund_df[fund_name_col].dropna()
    print(f"\n基金简称总数: {len(fund_names)}")
    print(f"唯一基金简称数: {fund_names.nunique()}")
    
    # 找出重复的基金简称
    duplicates = fund_names[fund_names.duplicated(keep=False)]
    duplicate_counts = fund_names.value_counts()
    
    print(f"\n重复的基金简称数量: {len(duplicates)}")
    print(f"有重复的基金简称种类数: {len(duplicate_counts[duplicate_counts > 1])}")
    
    # 显示重复最多的基金简称
    print("\n重复次数最多的基金简称 (前10个):")
    for fund_name, count in duplicate_counts.head(10).items():
        print(f"  {fund_name}: {count}次")
    
    # 显示所有重复的基金简称
    print("\n所有重复的基金简称:")
    for fund_name, count in duplicate_counts[duplicate_counts > 1].items():
        print(f"  {fund_name}: {count}次")
    
    # 去掉重复的基金简称，保留第一次出现的记录
    print("\n=== 去掉重复的基金简称 ===")
    fund_df_no_duplicates = fund_df.drop_duplicates(subset=[fund_name_col], keep='first')
    
    print(f"去重前数据形状: {fund_df.shape}")
    print(f"去重后数据形状: {fund_df_no_duplicates.shape}")
    print(f"去除了 {fund_df.shape[0] - fund_df_no_duplicates.shape[0]} 条重复记录")
    
    # 保存去重后的数据
    output_filename = 'govfund_filtered_no_duplicates.xlsx'
    fund_df_no_duplicates.to_excel(output_filename, index=False)
    print(f"\n去重后的数据已保存到: {output_filename}")
    
    # 验证去重结果
    remaining_fund_names = fund_df_no_duplicates[fund_name_col].dropna()
    print(f"\n去重后基金简称总数: {len(remaining_fund_names)}")
    print(f"去重后唯一基金简称数: {remaining_fund_names.nunique()}")
    
    # 检查是否还有重复
    remaining_duplicates = remaining_fund_names[remaining_fund_names.duplicated(keep=False)]
    if len(remaining_duplicates) == 0:
        print("✓ 去重成功！没有重复的基金简称了")
    else:
        print(f"⚠ 仍有 {len(remaining_duplicates)} 个重复的基金简称")
    