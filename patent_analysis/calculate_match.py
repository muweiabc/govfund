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
        
        unmatched_invest = invest_funds - govfund_funds 
        if unmatched_invest:
            print(f"\n未匹配的基金名称 (前10个):")
            for fund in list(unmatched_invest)[:10]:
                print(f"  - {fund}")
            if len(unmatched_invest) > 10:
                print(f"  ... 还有 {len(unmatched_invest) - 10} 个")
        
        return match_count, match_ratio, matched_funds
        
    except FileNotFoundError as e:
        print(f"错误: 找不到文件 - {e}")
        return None
    except Exception as e:
        print(f"处理数据时发生错误: {e}")
        return None

def calculate_investment_ratio():
    """
    计算invest文件中投资事件有多大比例是由govfund_filter中的政府引导基金投资的
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
        
        # 获取政府引导基金名称列表
        govfund_funds = set(govfund_df[fund_name_col_govfund].dropna().astype(str))
        print(f"\ngovfund_filtered中政府引导基金数量: {len(govfund_funds)}")
        
        # 统计投资事件总数
        total_investments = len(invest_df)
        print(f"invest中投资事件总数: {total_investments}")
        
        # 统计由政府引导基金投资的事件数量
        govfund_investments = 0
        govfund_investment_details = []
        
        for idx, row in invest_df.iterrows():
            fund_name = str(row[fund_name_col_invest]) if pd.notna(row[fund_name_col_invest]) else ""
            if fund_name in govfund_funds:
                govfund_investments += 1
                # 记录投资详情
                company = row.get('企业', 'N/A') if pd.notna(row.get('企业')) else 'N/A'
                investment_type = row.get('投资类型', 'N/A') if pd.notna(row.get('投资类型')) else 'N/A'
                investment_time = row.get('投资时间', 'N/A') if pd.notna(row.get('投资时间')) else 'N/A'
                govfund_investment_details.append({
                    '基金名称': fund_name,
                    '企业': company,
                    '投资类型': investment_type,
                    '投资时间': investment_time
                })
        
        # 计算比例
        govfund_investment_ratio = govfund_investments / total_investments if total_investments > 0 else 0
        
        print(f"\n=== 投资事件分析结果 ===")
        print(f"投资事件总数: {total_investments}")
        print(f"由政府引导基金投资的事件数: {govfund_investments}")
        print(f"政府引导基金投资比例: {govfund_investment_ratio:.2%}")
        
        # 显示由政府引导基金投资的事件详情
        if govfund_investment_details:
            print(f"\n由政府引导基金投资的事件详情 (前20个):")
            for i, detail in enumerate(govfund_investment_details[:20]):
                print(f"  {i+1}. 基金: {detail['基金名称']}")
                print(f"     企业: {detail['企业']}")
                print(f"     投资类型: {detail['投资类型']}")
                print(f"     投资时间: {detail['投资时间']}")
                print()
            
            if len(govfund_investment_details) > 20:
                print(f"  ... 还有 {len(govfund_investment_details) - 20} 个投资事件")
        
        # 统计各政府引导基金的投资频次
        fund_investment_count = {}
        for detail in govfund_investment_details:
            fund_name = detail['基金名称']
            fund_investment_count[fund_name] = fund_investment_count.get(fund_name, 0) + 1
        
        # 显示投资频次最高的政府引导基金
        if fund_investment_count:
            sorted_funds = sorted(fund_investment_count.items(), key=lambda x: x[1], reverse=True)
            print(f"\n投资频次最高的政府引导基金 (前10个):")
            for fund_name, count in sorted_funds[:10]:
                print(f"  {fund_name}: {count}次投资")
        
        return govfund_investments, total_investments, govfund_investment_ratio, govfund_investment_details
        
    except FileNotFoundError as e:
        print(f"错误: 找不到文件 - {e}")
        return None
    except Exception as e:
        print(f"处理数据时发生错误: {e}")
        return None

def analyze_non_govfund_investments():
    """
    分析invest中不在govfund_filter里的投资项
    """
    try:
        # 读取两个文件
        print("正在读取文件...")
        govfund_df = pd.read_excel('govfund_filtered.xlsx')
        invest_df = pd.read_excel('invest.xlsx')
        
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
        
        if fund_name_col_govfund is None or fund_name_col_invest is None:
            print("错误: 未找到必要的列名")
            return
        
        # 获取政府引导基金名称列表
        govfund_funds = set(govfund_df[fund_name_col_govfund].dropna().astype(str))
        print(f"govfund_filtered中政府引导基金数量: {len(govfund_funds)}")
        
        # 统计投资事件总数
        total_investments = len(invest_df)
        print(f"invest中投资事件总数: {total_investments}")
        
        # 统计不在政府引导基金中的投资事件
        non_govfund_investments = 0
        non_govfund_investment_details = []
        
        for idx, row in invest_df.iterrows():
            fund_name = str(row[fund_name_col_invest]) if pd.notna(row[fund_name_col_invest]) else ""
            if fund_name and fund_name not in govfund_funds:
                non_govfund_investments += 1
                # 记录投资详情
                company = row.get('企业', 'N/A') if pd.notna(row.get('企业')) else 'N/A'
                investment_type = row.get('投资类型', 'N/A') if pd.notna(row.get('投资类型')) else 'N/A'
                investment_time = row.get('投资时间', 'N/A') if pd.notna(row.get('投资时间')) else 'N/A'
                investment_amount = row.get('投资金额(RMB/M)', 'N/A') if pd.notna(row.get('投资金额(RMB/M)')) else 'N/A'
                industry = row.get('行业(清科)', 'N/A') if pd.notna(row.get('行业(清科)')) else 'N/A'
                region = row.get('地区', 'N/A') if pd.notna(row.get('地区')) else 'N/A'
                
                non_govfund_investment_details.append({
                    '基金名称': fund_name,
                    '企业': company,
                    '投资类型': investment_type,
                    '投资时间': investment_time,
                    '投资金额(RMB/M)': investment_amount,
                    '行业': industry,
                    '地区': region
                })
        
        # 计算比例
        non_govfund_investment_ratio = non_govfund_investments / total_investments if total_investments > 0 else 0
        
        print(f"\n=== 非政府引导基金投资事件分析结果 ===")
        print(f"投资事件总数: {total_investments}")
        print(f"非政府引导基金投资的事件数: {non_govfund_investments}")
        print(f"非政府引导基金投资比例: {non_govfund_investment_ratio:.2%}")
        
        # 显示非政府引导基金投资的事件详情
        if non_govfund_investment_details:
            print(f"\n非政府引导基金投资的事件详情 (前30个):")
            for i, detail in enumerate(non_govfund_investment_details[:30]):
                print(f"  {i+1}. 基金: {detail['基金名称']}")
                print(f"     企业: {detail['企业']}")
                print(f"     投资类型: {detail['投资类型']}")
                print(f"     投资时间: {detail['投资时间']}")
                print(f"     投资金额: {detail['投资金额(RMB/M)']}")
                print(f"     行业: {detail['行业']}")
                print(f"     地区: {detail['地区']}")
                print()
            
            if len(non_govfund_investment_details) > 30:
                print(f"  ... 还有 {len(non_govfund_investment_details) - 30} 个投资事件")
        
        # 统计各非政府引导基金的投资频次
        fund_investment_count = {}
        for detail in non_govfund_investment_details:
            fund_name = detail['基金名称']
            fund_investment_count[fund_name] = fund_investment_count.get(fund_name, 0) + 1
        
        # 显示投资频次最高的非政府引导基金
        if fund_investment_count:
            sorted_funds = sorted(fund_investment_count.items(), key=lambda x: x[1], reverse=True)
            print(f"\n投资频次最高的非政府引导基金 (前15个):")
            for fund_name, count in sorted_funds[:15]:
                print(f"  {fund_name}: {count}次投资")
        
        # 分析投资类型分布
        investment_type_count = {}
        for detail in non_govfund_investment_details:
            investment_type = detail['投资类型']
            investment_type_count[investment_type] = investment_type_count.get(investment_type, 0) + 1
        
        if investment_type_count:
            print(f"\n非政府引导基金投资类型分布 (前10个):")
            sorted_types = sorted(investment_type_count.items(), key=lambda x: x[1], reverse=True)
            for inv_type, count in sorted_types[:10]:
                print(f"  {inv_type}: {count}次")
        
        # 分析行业分布
        industry_count = {}
        for detail in non_govfund_investment_details:
            industry = detail['行业']
            industry_count[industry] = industry_count.get(industry, 0) + 1
        
        if industry_count:
            print(f"\n非政府引导基金投资行业分布 (前10个):")
            sorted_industries = sorted(industry_count.items(), key=lambda x: x[1], reverse=True)
            for industry, count in sorted_industries[:10]:
                print(f"  {industry}: {count}次")
        
        return non_govfund_investments, total_investments, non_govfund_investment_ratio, non_govfund_investment_details
        
    except FileNotFoundError as e:
        print(f"错误: 找不到文件 - {e}")
        return None
    except Exception as e:
        print(f"处理数据时发生错误: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("分析1: 基金名称匹配分析")
    print("=" * 60)
    result1 = calculate_fund_match()
    if result1:
        match_count, match_ratio, matched_funds = result1
        print(f"\n总结: 在govfund_filtered中有{match_count}个基金与invest文件匹配，匹配比例为{match_ratio:.2%}")
    
    print("\n" + "=" * 60)
    print("分析2: 投资事件中政府引导基金投资比例分析")
    print("=" * 60)
    result2 = calculate_investment_ratio()
    if result2:
        govfund_investments, total_investments, govfund_investment_ratio, govfund_investment_details = result2
        print(f"\n总结: 在{total_investments}个投资事件中，有{govfund_investments}个是由政府引导基金投资的，占比{govfund_investment_ratio:.2%}")
    
    print("\n" + "=" * 60)
    print("分析3: 非政府引导基金投资事件分析")
    print("=" * 60)
    result3 = analyze_non_govfund_investments()
    if result3:
        non_govfund_investments, total_investments, non_govfund_investment_ratio, non_govfund_investment_details = result3
        print(f"\n总结: 在{total_investments}个投资事件中，有{non_govfund_investments}个是由非政府引导基金投资的，占比{non_govfund_investment_ratio:.2%}") 