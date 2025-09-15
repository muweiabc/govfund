import pandas as pd

def analyze_fund_overlap():
    """
    读取invest.xlsx和govfund_filtered.xlsx，统计基金名称匹配的行数
    """
    try:
        # 读取投资事件数据
        print("正在读取 invest.xlsx...")
        invest_df = pd.read_excel('invest.xlsx')
        print(f"投资事件数据行数: {len(invest_df)}")
        print(f"投资事件数据列名: {list(invest_df.columns)}")
        
        # 读取政府引导基金数据
        print("\n正在读取 govfund_filtered.xlsx...")
        govfund_df = pd.read_excel('govfund_filtered.xlsx')
        print(f"政府引导基金数据行数: {len(govfund_df)}")
        print(f"政府引导基金数据列名: {list(govfund_df.columns)}")
        
        # 查找基金名称相关列
        invest_fund_col = None
        govfund_fund_col = None
        
        # 在投资事件数据中查找基金名称列
        for col in invest_df.columns:
            if '基金名称' in str(col):
                invest_fund_col = col
                break
        
        # 在政府引导基金数据中查找基金简称列
        for col in govfund_df.columns:
            if '基金简称' in str(col):
                govfund_fund_col = col
                break
        
        if invest_fund_col is None:
            print("错误: 在投资事件数据中未找到'基金名称'列")
            print("可用的列名:", list(invest_df.columns))
            return
        
        if govfund_fund_col is None:
            print("错误: 在政府引导基金数据中未找到'基金简称'列")
            print("可用的列名:", list(govfund_df.columns))
            return
        
        print(f"\n找到的列名:")
        print(f"投资事件基金名称列: {invest_fund_col}")
        print(f"政府引导基金简称列: {govfund_fund_col}")
        
        # 获取政府引导基金简称的唯一值集合
        govfund_fund_names = set(govfund_df[govfund_fund_col].dropna().unique())
        print(f"\n政府引导基金简称唯一值数量: {len(govfund_fund_names)}")
        
        # 统计匹配的行数
        invest_fund_names = invest_df[invest_fund_col].dropna()
        matched_rows = invest_df[invest_df[invest_fund_col].isin(govfund_fund_names)]
        
        print(f"\n=== 匹配结果 ===")
        print(f"投资事件数据总行数: {len(invest_df)}")
        print(f"投资事件数据中基金名称非空行数: {len(invest_fund_names)}")
        print(f"匹配的行数: {len(matched_rows)}")
        print(f"匹配率: {len(matched_rows)/len(invest_df)*100:.2f}%")
        
        # 显示一些匹配的示例
        print(f"\n匹配的基金名称示例:")
        matched_funds = matched_rows[invest_fund_col].unique()[:10]
        for fund in matched_funds:
            print(f"  - {fund}")
        
        # 显示一些不匹配的示例
        unmatched_rows = invest_df[~invest_df[invest_fund_col].isin(govfund_fund_names)]
        print(f"\n不匹配的基金名称示例:")
        unmatched_funds = unmatched_rows[invest_fund_col].dropna().unique()[:10]
        for fund in unmatched_funds:
            print(f"  - {fund}")
        
        return matched_rows, unmatched_rows
        
    except FileNotFoundError as e:
        print(f"文件未找到: {e}")
        return None, None
    except Exception as e:
        print(f"分析过程中发生错误: {e}")
        return None, None

def get_gdp(province, year, gdplist):
    row = gdplist[(gdplist['省级'] == province) & (gdplist['年份'] == year)]
    return row.iloc[:,2]

if __name__ == "__main__":
    # 分析基金名称匹配情况
    # matched_data, unmatched_data = analyze_fund_overlap()
    gdplist = pd.read_excel("gdp.xlsx")
    print(get_gdp('北京市',2021,gdplist))
