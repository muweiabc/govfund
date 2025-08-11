import pandas as pd

def calculate_fund_match():
    """
    计算govfund_filtered中基金简称匹配invest文件中基金名称的数量和比例
    """
    try:
        # 读取两个文件
        print("正在读取文件...")
        govfund_df = pd.read_excel('govfund_filtered.xlsx')
        invest_df = pd.read_excel('invest.xlsx')
        
        print(f"govfund_filtered数据形状: {govfund_df.shape}")
        print(f"invest数据形状: {invest_df.shape}")
        
        # 显示列名
        print(f"\ngovfund_filtered列名: {list(govfund_df.columns)}")
        print(f"invest列名: {list(invest_df.columns)}")
        
        # 查找基金简称列和基金名称列
        fund_name_col_govfund = None
        fund_name_col_invest = None
        
        # 在govfund中查找基金简称列
        for col in govfund_df.columns:
            if '基金简称' in str(col) or '基金名称' in str(col):
                fund_name_col_govfund = col
                break
        
        # 在invest中查找基金名称列
        for col in invest_df.columns:
            if '基金名称' in str(col) or '基金简称' in str(col):
                fund_name_col_invest = col
                break
        
        if fund_name_col_govfund is None:
            print("错误: 在govfund_filtered中未找到基金简称列")
            print("可用列名:", list(govfund_df.columns))
            return
        
        if fund_name_col_invest is None:
            print("错误: 在invest中未找到基金名称列")
            print("可用列名:", list(invest_df.columns))
            return
        
        print(f"\n使用列名:")
        print(f"govfund_filtered基金名称列: {fund_name_col_govfund}")
        print(f"invest基金名称列: {fund_name_col_invest}")
        
        # 获取基金名称列表
        govfund_funds = set(govfund_df[fund_name_col_govfund].dropna().astype(str))
        invest_funds = set(invest_df[fund_name_col_invest].dropna().astype(str))
        
        print(f"\ngovfund_filtered中基金数量: {len(govfund_funds)}")
        print(f"invest中基金数量: {len(invest_funds)}")
        
        # 计算匹配
        matched_funds = govfund_funds.intersection(invest_funds)
        match_count = len(matched_funds)
        match_ratio = match_count / len(govfund_funds) if len(govfund_funds) > 0 else 0
        
        print(f"\n=== 匹配结果 ===")
        print(f"匹配的基金数量: {match_count}")
        print(f"匹配比例: {match_ratio:.2%}")
        print(f"govfund_filtered中总基金数: {len(govfund_funds)}")
        
        # 显示匹配的基金名称
        if matched_funds:
            print(f"\n匹配的基金名称 (前10个):")
            for fund in list(matched_funds)[:10]:
                print(f"  - {fund}")
            if len(matched_funds) > 10:
                print(f"  ... 还有 {len(matched_funds) - 10} 个")
        
        # 显示未匹配的基金名称
        unmatched_govfund = govfund_funds - invest_funds
        if unmatched_govfund:
            print(f"\n未匹配的基金名称 (前10个):")
            for fund in list(unmatched_govfund)[:10]:
                print(f"  - {fund}")
            if len(unmatched_govfund) > 10:
                print(f"  ... 还有 {len(unmatched_govfund) - 10} 个")
        
        return match_count, match_ratio, matched_funds
        
    except FileNotFoundError as e:
        print(f"错误: 找不到文件 - {e}")
        return None
    except Exception as e:
        print(f"处理数据时发生错误: {e}")
        return None

if __name__ == "__main__":
    result = calculate_fund_match()
    if result:
        match_count, match_ratio, matched_funds = result
        print(f"\n总结: 在govfund_filtered中有{match_count}个基金与invest文件匹配，匹配比例为{match_ratio:.2%}") 