import pandas as pd
import numpy as np

def add_province_investment():
    first_investments_df = pd.read_excel('invest.xlsx', sheet_name='有专利公司首次投资')
    first_investments_df = first_investments_df[(first_investments_df['投资阶段'] != '--') & (~ first_investments_df['地区'].isna())]
    first_investments_df['省份'] = first_investments_df['地区'].str.split('|').str[1]
    with pd.ExcelWriter('invest.xlsx', engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        first_investments_df.to_excel(writer, sheet_name='有专利公司首次投资', index=False)

def invest_filter_province():
    first_investments_df = pd.read_excel('invest.xlsx', sheet_name='有专利公司首次投资')
    first_investments_df.dropna(subset=['省份'],inplace=True)
    first_investments_df = first_investments_df[first_investments_df['省份'] != '台湾']
    with pd.ExcelWriter('invest.xlsx', engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        first_investments_df.to_excel(writer, sheet_name='有专利公司首次投资', index=False)

def rename_urban():
    file = '2000-2023年各省份城镇化水平.xlsx'
    urban_df = pd.read_excel(file, sheet_name='原始版本')
    urban_df.rename(columns={'省份': '地区'}, inplace=True)
    with pd.ExcelWriter(file, engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        urban_df.to_excel(writer, sheet_name='原始版本', index=False)

def add_ln():
    df = pd.read_excel('patent_analysis/regression_panel_data.xlsx', sheet_name='面板数据')
    df['lnGDP'] = np.log(df['GDP'] + 1)
    df['lnFixedInvestment'] = np.log(df['固定资产投资'] + 1)

    with pd.ExcelWriter('patent_analysis/regression_panel_data.xlsx', engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='面板数据1', index=False)

if __name__ == "__main__":
    # add_province_investment()
    # invest_filter_province()
    add_ln()