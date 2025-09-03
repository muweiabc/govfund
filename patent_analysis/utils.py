import pandas as pd
import numpy as np

def add_province_investment():
    first_investments_df = pd.read_excel('invest.xlsx', sheet_name='有专利公司首次投资')
    first_investments_df = first_investments_df[(first_investments_df['投资阶段'] != '--') & (~ first_investments_df['地区'].isna())]
    first_investments_df['省份'] = first_investments_df['地区'].str.split('|').str[1]
    with pd.ExcelWriter('invest.xlsx', engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        first_investments_df.to_excel(writer, sheet_name='有专利公司首次投资', index=False)

if __name__ == "__main__":
    add_province_investment()