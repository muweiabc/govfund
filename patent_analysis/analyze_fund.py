import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

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

def fund_clean():
    """
    
     从invest中提取被投资企业所在省份
    """
    FUND_FILE = 'govfund_filtered.xlsx'
    df = pd.read_excel(FUND_FILE)
    df['成立时间'] = pd.to_datetime(df['成立时间'], errors='coerce')
    df = df.dropna(subset=['成立时间'])  # 删除无法转换的日期
    
    df['成立年份'] = df['成立时间'].dt.year
    def extract_province(region):
        # 处理"中国|省份|城市|区县"格式
        parts = str(region).split('|')
        if len(parts) >= 2:
            return parts[1]  # 返回省份部分
        else:
            return region
    filtered_df = df[(df['注册地区'] != '--') & (df['注册地区']!='中国') ]
    filtered_df['省份'] = filtered_df['注册地区'].apply(extract_province)

    with pd.ExcelWriter(FUND_FILE, engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        # 保存面板数据
        filtered_df.to_excel(writer, sheet_name='fund处理', index=False)

def read_invest_panel():
    df = pd.read_excel('invest.xlsx',sheet_name='基金所属省份')
    return df

def write_invest_panel(df, sheet):
    with pd.ExcelWriter('invest.xlsx', engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet, index=False)

def add_group_tag(df):
    """
     添加投资基金和被投企业省份是否相同标签
    """
    def compare(row):
        p1,p2 = row['省份'], row['基金所属省份']
        if p1.endswith('市') or p1.endswith('省'):
            p1 = p1[0:-1]
        return p1==p2

    df['same_location'] = df.apply(compare,axis=1)
    return df


def fund_time_and_spatial():
    """
    分析政府引导基金的时间和空间分布
    绘制基金成立年份分布图和省份分布图
    """

    # 读取数据
    df = pd.read_excel('govfund_filtered.xlsx', sheet_name='fund处理')
    
    # 将成立时间转换为日期时间格式
    # df['成立时间'] = pd.to_datetime(df['成立时间'], errors='coerce')
    # df = df.dropna(subset=['成立时间'])  # 删除无法转换的日期
    
    # df['成立年份'] = df['成立时间'].dt.year
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 1. 基金成立年份分布图
    fund_found_year = df['成立年份'].value_counts().sort_index()
    
    ax1.bar(fund_found_year.index, fund_found_year.values, 
            color='skyblue', edgecolor='navy', alpha=0.7)
    ax1.set_xlabel('成立年份')
    ax1.set_ylabel('基金数量')
    ax1.set_title('政府引导基金成立时间', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 添加数值标签
    for i, v in enumerate(fund_found_year.values):
        ax1.text(fund_found_year.index[i], v + 0.5, str(v), 
                ha='center', va='bottom', fontsize=10)
    
    # 2. 基金省份分布图
    # 处理注册地区数据，提取省份信息
    
    fund_province = df['省份'].value_counts()
    
    # 只显示前15个省份，其他归为"其他"
    top_provinces = fund_province.head(15)
    other_count = fund_province.iloc[15:].sum()
    
    if other_count > 0:
        top_provinces['其他'] = other_count
    
    # 创建饼图
    colors = plt.cm.Set3(np.linspace(0, 1, len(top_provinces)))
    wedges, texts, autotexts = ax2.pie(top_provinces.values, 
                                      labels=top_provinces.index,
                                      autopct='%1.1f%%',
                                      colors=colors,
                                      startangle=90)
    
    ax2.set_title('政府引导基金所属省份', fontsize=14, fontweight='bold')
    
    # 调整标签位置，避免重叠
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('patent_analysis/graph/fund_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 创建更详细的年份分布图（柱状图）
    plt.figure(figsize=(12, 6))
    bars = plt.bar(fund_found_year.index, fund_found_year.values, 
                   color='lightcoral', edgecolor='darkred', alpha=0.7)
    plt.xlabel('成立年份', fontsize=12)
    plt.ylabel('基金数量', fontsize=12)
    plt.title('政府引导基金成立时间分布（详细版）', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('patent_analysis/graph/fund_year_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 创建省份分布柱状图
    plt.figure(figsize=(14, 8))
    top_20_provinces = fund_province.head(20)
    bars = plt.bar(range(len(top_20_provinces)), top_20_provinces.values,
                   color='lightgreen', edgecolor='darkgreen', alpha=0.7)
    plt.xlabel('省份', fontsize=12)
    plt.ylabel('基金数量', fontsize=12)
    plt.title('政府引导基金省份分布（前20）', fontsize=14, fontweight='bold')
    plt.xticks(range(len(top_20_provinces)), top_20_provinces.index, rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 添加数值标签
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('patent_analysis/graph/fund_province_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 打印统计信息
    print("=== 政府引导基金时间和空间分布分析 ===")
    print(f"总基金数量: {len(df)}")
    print(f"成立年份范围: {df['成立年份'].min()} - {df['成立年份'].max()}")
    print(f"涉及省份数量: {df['省份'].nunique()}")
    
    print("\n=== 成立年份分布 ===")
    print(fund_found_year.sort_index())
    
    print("\n=== 省份分布 (前10) ===")
    print(fund_province.head(10))
    
    return fund_found_year, fund_province

def patent_analysis():
    """
    分析专利数据的时间和类型分布
    绘制专利申请时间分布柱状图和专利类型饼图
    保存结果到patent_analysis.xlsx
    """
    print("=== 专利数据分析 ===")
    
    # 读取专利数据
    print("正在读取专利数据...")
    df = pd.read_csv('data/trimpatent_all.csv')
    print(f"专利数据总行数: {len(df):,}")
    print(f"专利数据列名: {list(df.columns)}")
    
    # 数据预处理
    print("正在预处理数据...")
    
    # 处理申请年份
    df['申请年份'] = pd.to_numeric(df['申请年份'], errors='coerce')
    df = df.dropna(subset=['申请年份'])
    df['申请年份'] = df['申请年份'].astype(int)
    
    # 处理专利类型
    df['专利类型'] = df['专利类型'].fillna('未知')
    
    print(f"有效专利数据行数: {len(df):,}")
    print(f"申请年份范围: {df['申请年份'].min()} - {df['申请年份'].max()}")
    print(f"专利类型数量: {df['专利类型'].nunique()}")
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 1. 专利申请时间分布柱状图
    print("正在生成专利申请时间分布图...")
    patent_year = df['申请年份'].value_counts().sort_index()
    
    # 只显示2000年之后的数据
    patent_year = patent_year[patent_year.index >= 2000]
    
    bars = ax1.bar(patent_year.index, patent_year.values, 
                   color='lightblue', edgecolor='navy', alpha=0.7)
    ax1.set_xlabel('申请年份', fontsize=12)
    ax1.set_ylabel('专利数量', fontsize=12)
    ax1.set_title('专利申请时间分布', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 添加数值标签（只对较大的值显示）
    for i, (year, count) in enumerate(patent_year.items()):
        if count > patent_year.max() * 0.05:  # 只显示大于最大值5%的标签
            ax1.text(year, count + patent_year.max() * 0.01, f'{count:,}', 
                    ha='center', va='bottom', fontsize=8, rotation=45)
    
    # 设置x轴刻度
    ax1.set_xticks(range(2000, 2025, 5))
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. 专利类型分布饼图
    print("正在生成专利类型分布图...")
    patent_type = df['专利类型'].value_counts()
    
    # 只显示前8个类型，其他归为"其他"
    top_types = patent_type.head(8)
    other_count = patent_type.iloc[8:].sum()
    
    if other_count > 0:
        top_types['其他'] = other_count
    
    # 创建饼图
    colors = plt.cm.Set3(np.linspace(0, 1, len(top_types)))
    wedges, texts, autotexts = ax2.pie(top_types.values, 
                                      labels=top_types.index,
                                      autopct='%1.1f%%',
                                      colors=colors,
                                      startangle=90)
    
    ax2.set_title('专利类型分布', fontsize=14, fontweight='bold')
    
    # 调整标签位置，避免重叠
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('patent_analysis/graph/patent_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 创建更详细的年份分布图
    plt.figure(figsize=(14, 8))
    bars = plt.bar(patent_year.index, patent_year.values, 
                   color='lightcoral', edgecolor='darkred', alpha=0.7)
    plt.xlabel('申请年份', fontsize=12)
    plt.ylabel('专利数量', fontsize=12)
    plt.title('专利申请时间分布（详细版）', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # 添加数值标签
    for i, (year, count) in enumerate(patent_year.items()):
        if i % 3 == 0:  # 每3年显示一个标签
            plt.text(year, count + patent_year.max() * 0.01, f'{count:,}', 
                    ha='center', va='bottom', fontsize=8, rotation=45)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('patent_analysis/graph/patent_year_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 创建专利类型分布柱状图
    plt.figure(figsize=(12, 8))
    top_15_types = patent_type.head(15)
    bars = plt.bar(range(len(top_15_types)), top_15_types.values,
                   color='lightgreen', edgecolor='darkgreen', alpha=0.7)
    plt.xlabel('专利类型', fontsize=12)
    plt.ylabel('专利数量', fontsize=12)
    plt.title('专利类型分布（前15）', fontsize=14, fontweight='bold')
    plt.xticks(range(len(top_15_types)), top_15_types.index, rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 添加数值标签
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + height * 0.01,
                f'{int(height):,}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('patent_analysis/graph/patent_type_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 保存结果到Excel文件
    print("正在保存结果到Excel文件...")
    
    with pd.ExcelWriter('patent_analysis/patent_analysis.xlsx', engine='openpyxl') as writer:
        # 1. 年份分布统计
        year_stats = pd.DataFrame({
            '申请年份': patent_year.index,
            '专利数量': patent_year.values,
            '占比(%)': (patent_year.values / patent_year.sum() * 100).round(2)
        })
        year_stats.to_excel(writer, sheet_name='申请年份分布', index=False)
        
        # 2. 专利类型分布统计
        type_stats = pd.DataFrame({
            '专利类型': patent_type.index,
            '专利数量': patent_type.values,
            '占比(%)': (patent_type.values / patent_type.sum() * 100).round(2)
        })
        type_stats.to_excel(writer, sheet_name='专利类型分布', index=False)
        
        # 3. 年度专利类型交叉统计
        year_type_cross = pd.crosstab(df['申请年份'], df['专利类型'])
        year_type_cross.to_excel(writer, sheet_name='年度专利类型交叉表')
        
        # 4. 专利类型年度趋势
        type_trend = df.groupby(['申请年份', '专利类型']).size().unstack(fill_value=0)
        type_trend.to_excel(writer, sheet_name='专利类型年度趋势')
        
        # 5. 数据摘要
        summary_data = {
            '统计指标': [
                '总专利数量',
                '申请年份范围',
                '专利类型数量',
                '平均每年专利数量',
                '专利数量最多的年份',
                '专利数量最多的类型'
            ],
            '数值': [
                f"{len(df):,}",
                f"{df['申请年份'].min()}-{df['申请年份'].max()}",
                f"{df['专利类型'].nunique()}",
                f"{len(df) / (df['申请年份'].max() - df['申请年份'].min() + 1):,.0f}",
                f"{patent_year.idxmax()} ({patent_year.max():,}件)",
                f"{patent_type.index[0]} ({patent_type.iloc[0]:,}件)"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='数据摘要', index=False)
    
    # 打印统计信息
    print("\n=== 专利数据分析结果 ===")
    print(f"总专利数量: {len(df):,}")
    print(f"申请年份范围: {df['申请年份'].min()} - {df['申请年份'].max()}")
    print(f"专利类型数量: {df['专利类型'].nunique()}")
    
    print("\n=== 申请年份分布 (前10) ===")
    print(patent_year.head(10))
    
    print("\n=== 专利类型分布 (前10) ===")
    print(patent_type.head(10))
    
    print(f"\n结果已保存到: patent_analysis/patent_analysis.xlsx")
    
    
    return patent_year, patent_type

def fund_location():
    """
     提取投资基金所在省份
    """
    file = 'invest.xlsx'

    # 2. 读取文件（假设文件已上传并可访问）
    try:
        # 假设文件内容已经加载到环境中
        df = pd.read_excel(file,sheet_name='有专利公司首次投资')
    except FileNotFoundError:
        # 实际使用中，如果文件路径不可用，会在这里失败。
        # 为了演示，我将使用一个示例数据框模拟加载后的情况。
        print(f"注意：文件 无法直接访问。")
        

    # 3. 定义省份和城市映射规则
    # 包含所有省、自治区、直辖市、特别行政区的名称（避免使用简称如“蒙”、“宁”、“新”等）
    provinces = [
        '北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '上海', 
        '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', 
        '广东', '广西', '海南', '重庆', '四川', '贵州', '云南', '西藏', '陕西', 
        '甘肃', '青海', '宁夏', '新疆', '香港', '澳门', '台湾'
    ]

    # 重点城市到省份的映射 (用于避免只出现城市名但属于某个省份的情况)
    city_to_province = {
        # **直辖市/特别行政区 (保留，以便名称中出现'市'也能正确识别)**
        '北京': '北京', '天津': '天津', '上海': '上海', '重庆': '重庆', 
        '香港': '香港', '澳门': '澳门',
        
        # **华北地区**
        '石家庄': '河北', '太原': '山西', '呼和浩特': '内蒙古','鄂尔多斯': '内蒙古',
        
        # **东北地区** (副省级市: 沈阳, 大连, 哈尔滨, 长春)
        '沈阳': '辽宁', '大连': '辽宁', '长春': '吉林', '哈尔滨': '黑龙江',
        
        # **华东地区** (省会和计划单列市: 南京, 杭州, 济南, 青岛, 厦门, 宁波)
        '南京': '江苏', '苏州': '江苏', '无锡': '江苏', '杭州': '浙江', '宁波': '浙江', '合肥': '安徽',
        '福州': '福建', '厦门': '福建', '南昌': '江西', '济南': '山东', '青岛': '山东',
        
        # **华中地区** (省会城市)
        '郑州': '河南', '武汉': '湖北', '长沙': '湖南',
        
        # **华南地区** (省会和副省级市: 广州, 深圳)
        '广州': '广东', '深圳': '广东', '南宁': '广西', '海口': '海南',
        
        # **西南地区** (省会和副省级市: 成都)
        '成都': '四川', '贵阳': '贵州', '昆明': '云南', '拉萨': '西藏',
        
        # **西北地区** (省会城市)
        '西安': '陕西', '兰州': '甘肃', '西宁': '青海', '银川': '宁夏', '乌鲁木齐': '新疆',
        
        # **台湾（作为地区处理）**
        '台北': '台湾', '高雄': '台湾',
    }

    # 合并所有关键词，优先匹配城市，其次匹配省份
    keywords = {**city_to_province, **{p: p for p in provinces}}

    # 4. 定义识别函数
    def identify_province(fund_name):
        # 优先匹配城市，然后映射到省份
        for city, province in city_to_province.items():
            if city in fund_name:
                return province

        # 匹配省份/直辖市/自治区/特别行政区
        for p in provinces:
            if p in fund_name:
                # 对于自治区，返回其简称，如“内蒙古”
                return p
        
        # 兜底处理：如果名称中含有“国家”、“中央”、“中国”或“全国”，统一标记为“中央级”
        # 注意：根据用户要求，这里将中央级的也标记为“缺失”
        # if any(k in fund_name for k in ['国家', '中央', '中国', '全国']):
        #     return '中央级'

        return

    # 5. 应用函数创建新字段
    df['基金所属省份'] = df['投资方全称'].apply(identify_province)
    df.dropna(subset=['基金所属省份'],inplace=True)

    # 6. 显示结果
    print("--- 原始数据（部分）与新字段结果 ---")
    print(df[['投资方全称', '基金所属省份']].head(10))

    with pd.ExcelWriter(file, engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='基金所属省份', index=False)


def main():
    # 分析基金时间和空间分布
    fund_time_and_spatial()
    
    # 分析专利数据
    # patent_analysis()
    # fund_clean()
    # df = read_invest_panel()
    # df = add_group_tag(df)
    # write_invest_panel(df, 'location')
    # fund_location()

if __name__ == "__main__":
    main()
