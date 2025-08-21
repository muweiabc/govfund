import pandas as pd

# 查看invest.xlsx文件结构
print("=== invest.xlsx 文件结构 ===")
try:
    invest_df = pd.read_excel('invest.xlsx')
    print(f"行数: {len(invest_df)}")
    print(f"列数: {len(invest_df.columns)}")
    print("列名:")
    for i, col in enumerate(invest_df.columns):
        print(f"  {i+1}. {col}")
    
    print("\n前5行数据:")
    print(invest_df.head())
    
    print("\n数据类型:")
    print(invest_df.dtypes)
    
except Exception as e:
    print(f"读取invest.xlsx出错: {e}")

print("\n" + "="*50 + "\n")

# 查看company_patent_yearly.xlsx文件结构
print("=== company_patent_yearly.xlsx 文件结构 ===")
try:
    patent_df = pd.read_excel('company_patent_yearly.xlsx')
    print(f"行数: {len(patent_df)}")
    print(f"列数: {len(patent_df.columns)}")
    print("列名:")
    for i, col in enumerate(patent_df.columns):
        print(f"  {i+1}. {col}")
    
    print("\n前5行数据:")
    print(patent_df.head())
    
    print("\n数据类型:")
    print(patent_df.dtypes)
    
except Exception as e:
    print(f"读取company_patent_yearly.xlsx出错: {e}")
