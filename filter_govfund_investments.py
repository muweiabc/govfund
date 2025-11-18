import pandas as pd
import os
import warnings
import argparse
warnings.filterwarnings('ignore')

def filter_govfund_investments():
    """过滤政府投资基金的投资数据"""
    try:
        print("=== 政府投资基金投资数据过滤 ===")
        
        # 检查必要文件
        required_files = ['govfund_filtered.xlsx', 'invest.xlsx', 'govfund_analysis_results.xlsx']
        for file in required_files:
            if not os.path.exists(file):
                print(f"✗ 错误: 找不到文件 {file}")
                return False
        
        # 1. 读取政府投资基金数据
        print("\n1. 读取政府投资基金数据...")
        govfund_df = pd.read_excel('govfund_filtered.xlsx')
        print(f"   govfund_filtered.xlsx 形状: {govfund_df.shape}")
        
        # 提取基金简称列表
        govfund_names = govfund_df['基金简称'].dropna().unique().tolist()
        print(f"   政府投资基金数量: {len(govfund_names)}")
        print(f"   前5个基金简称: {govfund_names[:5]}")
        
        # 2. 读取投资数据
        print("\n2. 读取投资数据...")
        invest_df = pd.read_excel('invest.xlsx')
        print(f"   invest.xlsx 形状: {invest_df.shape}")
        
        # 检查基金名称列
        fund_name_cols = ['基金名称', '基金全称']
        available_cols = [col for col in fund_name_cols if col in invest_df.columns]
        
        if not available_cols:
            print("✗ 错误: 投资数据中没有找到基金名称相关的列")
            return False
        
        print(f"   可用的基金名称列: {available_cols}")
        
        # 3. 过滤政府投资基金的投资数据
        print("\n3. 过滤政府投资基金的投资数据...")
        
        # 创建过滤条件
        filtered_data = []
        total_matches = 0
        
        for idx, row in invest_df.iterrows():
            is_govfund = False
            matched_fund = None
            
            # 检查基金名称列是否匹配政府投资基金
            for col in available_cols:
                if pd.notna(row[col]):
                    fund_name = str(row[col])
                    for govfund_name in govfund_names:
                        if govfund_name in fund_name or fund_name in govfund_name:
                            is_govfund = True
                            matched_fund = govfund_name
                            break
                    if is_govfund:
                        break
            
            if is_govfund:
                total_matches += 1
                # 添加匹配的政府投资基金名称
                row_dict = row.to_dict()
                row_dict['匹配的政府投资基金'] = matched_fund
                filtered_data.append(row_dict)
        
        print(f"   匹配的投资记录数: {total_matches}")
        print(f"   匹配率: {total_matches/len(invest_df)*100:.2f}%")
        
        # 4. 创建结果DataFrame
        if filtered_data:
            result_df = pd.DataFrame(filtered_data)
            print(f"\n4. 结果数据统计:")
            print(f"   结果数据形状: {result_df.shape}")
            print(f"   列数: {len(result_df.columns)}")
            
            # 5. 输出到Excel文件
            print("\n5. 输出结果到Excel文件...")
            
            # 读取现有的Excel文件
            with pd.ExcelWriter('govfund_analysis_results.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
                result_df.to_excel(writer, sheet_name='政府投资基金投资数据', index=False)
            
            print("✓ 成功将结果输出到 '政府投资基金投资数据' 标签页")
            
            # 显示结果预览
            print(f"\n6. 结果数据预览:")
            print(f"   前5行数据:")
            print(result_df[['投资方', '基金名称', '企业', '投资金额(RMB/M)', '匹配的政府投资基金']].head())
            
            # 统计信息
            print(f"\n7. 统计信息:")
            print(f"   涉及的政府投资基金数量: {result_df['匹配的政府投资基金'].nunique()}")
            print(f"   投资企业数量: {result_df['企业'].nunique()}")
            print(f"   投资金额统计:")
            if '投资金额(RMB/M)' in result_df.columns:
                amount_col = '投资金额(RMB/M)'
                numeric_amounts = pd.to_numeric(result_df[amount_col], errors='coerce').dropna()
                if len(numeric_amounts) > 0:
                    print(f"     总金额: {numeric_amounts.sum():.2f} M")
                    print(f"     平均金额: {numeric_amounts.mean():.2f} M")
                    print(f"     最大金额: {numeric_amounts.max():.2f} M")
                    print(f"     最小金额: {numeric_amounts.min():.2f} M")
            
            return True
        else:
            print("✗ 没有找到匹配的政府投资基金投资数据")
            return False
            
    except Exception as e:
        print(f"✗ 处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_investments_by_province_year():
    """分析政府投资基金投资数据，按省份和年份统计投资笔数"""
    try:
        print("=== 政府投资基金投资数据省份年份统计 ===")
        
        # 检查文件是否存在
        if not os.path.exists('govfund_analysis_results.xlsx'):
            print("✗ 错误: 找不到文件 govfund_analysis_results.xlsx")
            return False
        
        # 读取政府投资基金投资数据
        print("\n1. 读取政府投资基金投资数据...")
        df = pd.read_excel('govfund_analysis_results.xlsx', sheet_name='分省政府投资基金')
        print(f"   数据形状: {df.shape}")
        
        # 检查必要的列
        required_columns = ['省份', '投资时间']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"✗ 错误: 缺少必要的列: {missing_columns}")
            print(f"   可用的列: {list(df.columns)}")
            return False
        
        # 2. 数据预处理
        print("\n2. 数据预处理...")
        
        # 处理地区列 - 提取省份信息
        def extract_province(region):
            if pd.isna(region):
                return '未知'
            
            region_str = str(region)
            # 常见的省份后缀
            suffixes = ['省', '市', '自治区', '特别行政区']
            for suffix in suffixes:
                if region_str.endswith(suffix):
                    return region_str[:-len(suffix)]
            return region_str
        
        # 处理投资时间列 - 提取年份
        def extract_year(investment_time):
            if pd.isna(investment_time):
                return '未知'
            
            time_str = str(investment_time)
            # 尝试提取年份
            import re
            year_match = re.search(r'(\d{4})', time_str)
            if year_match:
                return int(year_match.group(1))
            return '未知'
        
        # 应用转换
        # df['省份'] = df['地区'].apply(extract_province)
        df['投资年份'] = df['投资时间'].apply(extract_year)
        
        # 过滤掉无效数据
        valid_df = df[(df['省份'] != '未知') & (df['投资年份'] != '未知')].copy()
        print(f"   有效数据记录数: {len(valid_df)}")
        print(f"   省份数量: {valid_df['省份'].nunique()}")
        print(f"   年份范围: {valid_df['投资年份'].min()} - {valid_df['投资年份'].max()}")
        
        # 3. 按省份和年份统计
        print("\n3. 按省份和年份统计投资笔数...")
        
        # 创建透视表
        pivot_table = valid_df.pivot_table(
            index='省份', 
            columns='投资年份', 
            values='投资方',  # 使用投资方列来计数
            aggfunc='count',
            fill_value=0
        )
        
        # 添加总计列和行
        pivot_table['总计'] = pivot_table.sum(axis=1)
        pivot_table.loc['总计'] = pivot_table.sum()
        
        print(f"   统计表形状: {pivot_table.shape}")
        
        # 4. 输出结果到Excel
        print("\n4. 输出统计结果到Excel...")
        
        # 创建详细统计信息
        summary_stats = []
        for province in valid_df['省份'].unique():
            province_data = valid_df[valid_df['省份'] == province]
            for year in sorted(valid_df['投资年份'].unique()):
                year_data = province_data[province_data['投资年份'] == year]
                if len(year_data) > 0:
                    summary_stats.append({
                        '省份': province,
                        '年份': year,
                        '投资笔数': len(year_data),
                        '投资企业数': year_data['企业'].nunique(),
                        '投资金额(M)': year_data['投资金额(RMB/M)'].apply(
                            lambda x: pd.to_numeric(x, errors='coerce')
                        ).sum()
                    })
        
        summary_df = pd.DataFrame(summary_stats)
        
        # 输出到Excel文件
        with pd.ExcelWriter('govfund_analysis_results.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            pivot_table.to_excel(writer, sheet_name='省份年份投资统计', index=True)
            summary_df.to_excel(writer, sheet_name='省份年份投资详情', index=False)
        
        print("✓ 成功输出统计结果到Excel文件")
        print(f"   - 省份年份投资统计 (透视表)")
        print(f"   - 省份年份投资详情 (详细数据)")
        
        # 5. 显示统计结果
        print(f"\n5. 统计结果预览:")
        print(f"   投资笔数最多的前5个省份:")
        top_provinces = pivot_table['总计'].sort_values(ascending=False).head(6)  # 排除总计行
        for province, count in top_provinces.items():
            if province != '总计':
                print(f"     {province}: {count} 笔")
        
        print(f"\n   投资笔数最多的前5个年份:")
        year_totals = pivot_table.loc['总计'].sort_values(ascending=False).head(6)  # 排除总计列
        for year, count in year_totals.items():
            if year != '总计':
                print(f"     {year}年: {count} 笔")
        
        # 6. 保存统计结果到CSV文件（便于进一步分析）
        pivot_table.to_csv('省份年份投资统计.csv', encoding='utf-8-sig')
        summary_df.to_csv('省份年份投资详情.csv', encoding='utf-8-sig', index=False)
        print(f"\n6. 同时保存CSV格式文件:")
        print(f"   - 省份年份投资统计.csv")
        print(f"   - 省份年份投资详情.csv")
        
        return True
        
    except Exception as e:
        print(f"✗ 统计过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_govfund_investments():
    """获取政府投资基金投资数据"""
    invest_df = pd.read_csv('invest_w_index.csv',index_col=0)
    govfund_df = pd.read_csv('govfund_w_index.csv',index_col=0)
    invest_by_govfund = []

    fundname_to_fundrow = {}
    for idx, row in govfund_df.iterrows():
        fundname_to_fundrow[row['基金简称']] = row

    for idx, row in invest_df.iterrows():
        fund_name = row['基金名称']
        if fund_name in fundname_to_fundrow:
            fundrow = fundname_to_fundrow[fund_name]
            row['匹配的政府投资基金index'] = fundrow.name
            row['国资背景'] = fundrow['管理机构是否国资']
            
            invest_by_govfund.append(row)
            
        # for jdx, row_govfund in govfund_df.iterrows():
        #     if  fund_name.strip() == row_govfund['基金简称'].strip():
        #         row['匹配的政府投资基金index'] = row_govfund.name
        #         row['国资背景'] = row_govfund['管理机构是否国资']
        #         matched = True
        #         invest_filtered.append(row)
        #         break
    invest_filtered_df = pd.DataFrame(invest_by_govfund)      
    invest_filtered_df.to_csv('invest_by_govfund.csv', index=False)
    return invest_filtered_df

def add_index_to_df():
    invest_df = pd.read_excel('invest.xlsx', sheet_name='所有投资')
    # invest_df['index'] = range(1, len(invest_df) + 1)
    invest_df.to_csv('invest_w_index.csv', index=True)
    govfund_df = pd.read_excel('govfund_filtered.xlsx', sheet_name='合并数据')
    # invest_df['index'] = range(1, len(invest_df) + 1)
    govfund_df.to_csv('govfund_w_index.csv', index=True)

def get_investments_by_province_year():
    """获取按省份和年份统计的投资笔数"""

def filter_regression_data():
    invest_df = pd.read_csv('invest_by_govfund.csv',index_col=0)
    panel_df = pd.read_excel('patent_analysis/regression_panel_data.xlsx', sheet_name='面板数据')
    # company_to_invest = {}
    invest_df.set_index('融资主体', inplace=True)
    panel_data = pd.DataFrame()
    for i in range(int(len(panel_df)/6)):
        company = panel_df.iloc[i*6]['company']
        try:
            block = panel_df.iloc[i*6:(i+1)*6]
            block['国资背景'] = invest_df.loc[company]['国资背景']
            # panel_data.append(block)
            panel_data = pd.concat([panel_data,block],ignore_index=True)
            print(123)
        except:
            pass
    
    panel_data.to_csv('panel_data_govfund.csv')

def main():
    args = argparse.ArgumentParser()
    args.add_argument('--myfunc', help='函数名')
    args = args.parse_args()
    if args.myfunc == 'add_index_to_df':
        add_index_to_df()
    elif args.myfunc == 'get_govfund_investments':
        get_govfund_investments()
    elif args.myfunc == 'filter_regression_data':
        filter_regression_data()

if __name__ == "__main__":
    # main()
    # success = filter_govfund_investments()
    # get_govfund_investments()
    filter_regression_data()
            