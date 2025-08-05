import pandas as pd

# 读取投资事件数据
invest_df = pd.read_excel('invest.xlsx')

# 获取'融资主体'列的前5个非空值
col = invest_df['融资主体']
first_5_values = col.dropna().head(5).tolist()

# 用OR连接前5个值
or_query = " OR ".join([f'"{value}"' for value in first_5_values])

print("前5个融资主体值:")
for i, value in enumerate(first_5_values, 1):
    print(f"{i}. {value}")

print(f"\nOR查询语句:")
print(or_query) 