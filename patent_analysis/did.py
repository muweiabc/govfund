import pandas as pd
import numpy as np
import sys
sys.path.append('.')

# def filter_data():
#     provinces = set(['上海市', '天津市', '江苏省', '浙江省', '广东省', '重庆市', '北京市', '福建省', '河北省',
#        '湖北省', '海南省', '山东省', '吉林省', '河南省', '辽宁省', '安徽省', '四川省', '湖南省',
#        '江西省', '陕西省', '云南省', '甘肃省', '贵州省', '山西省', '黑龙江省','宁夏', '广西',
#        '新疆', '内蒙古', '青海省'])
#     df = pd.read_excel('regress_data_with_gdp.xlsx', sheet_name='回归数据')
#     df = df[df['省份'].isin(provinces)]
#     with pd.ExcelWriter('regress_data_with_gdp.xlsx', engine='openpyxl') as writer:
#         df.to_excel(writer, sheet_name='回归数据')

def _generate_dummy_variables(data_type,panel_df):
    """
    生成虚拟变量
    
    参数:
    panel_df: 面板数据DataFrame

    """
    print("生成虚拟变量...")
    
    
    # 添加交互项
    panel_df['treatment_post'] = panel_df['treatment'] * panel_df['post']
    
    
    
    province_cols = panel_df['省份']
    # 使用pd.get_dummies创建省份虚拟变量
    panel_dummies = pd.get_dummies(panel_df, columns=['省份','投资阶段'], prefix=['省','投资阶段'], drop_first=True, dtype=int)
    panel_dummies['原省份'] = province_cols
    print("   - 创建虚拟变量完成 ")
    return panel_dummies


def _perform_regression(data_type, province_dummy, stage_dummy):
    """
    执行DID回归分析
    
    参数:
    panel_df: 面板数据DataFrame
    enable_province_dummies: 是否启用省份虚拟变量
    
    返回:
    results: 回归结果
    """
    print("执行DID回归...")
    panel_df = read_panel_data(data_type)
    panel_df.set_index(['company', 'year'], inplace=True)
    
    from linearmodels import PanelOLS
    
    # 准备回归变量
    control_vars = ['treatment','treatment_post', 'gdp','城镇化率','ln_固定资产投资','二产比例','二产就业比例']
    
    province_cols = []
    if province_dummy:
        for col in panel_df.columns:
            if col.startswith('省'):
                control_vars.append(col)
                province_cols.append(col)
    stage_cols = []
    if stage_dummy:
        for col in panel_df.columns:
            if col.startswith('投资阶段'):
                control_vars.append(col)
                stage_cols.append(col)
    
    
    X = panel_df[control_vars]
    if data_type == 'patent':
        y = panel_df['ln_patents_plus_1']
    else:
        y = panel_df['ln_citations_plus_1']
    stas_x = X.describe()
    stas_y =y.describe()
    path = 'patent_analysis/'
    output_file = path + 'did_results'+ '_' + data_type + '.xlsx'
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        stas_x.to_excel(writer, sheet_name='回归变量描述性统计')
        stas_y.to_excel(writer, sheet_name='被解释变量描述性统计')

    print(f"   - 回归变量数量: {len(control_vars)}")
    print(f"   - 控制变量: {control_vars}")
    
    # 执行PanelOLS回归
    model = PanelOLS(y, X, entity_effects=False, time_effects=True)
    results = model.fit(cov_type='clustered', cluster_entity=True)
    
    print("   - 回归完成")
    print(f"   - 样本数: {len(panel_df):,}")
    print(f"   - 公司数: {panel_df.index.get_level_values('company').nunique():,}")
    
    # 显示回归结果
    print("\n回归结果:")
    print("=" * 80)
    print(results)
    print("=" * 80)

    
    # 显示省份虚拟变量的显著性（如果启用）
    significant_province_dummies = []
    if province_dummy:
        for col in province_cols:
            if col in results.params.index:
                p_value = results.pvalues[col]
                if p_value < 0.05:
                    significant_province_dummies.append((col, results.params[col], p_value))

    else:
        print(f"\n省份虚拟变量已禁用")
    
    # 计算边际效应
    print(f"\n边际效应分析:")
    # 控制组在投资前后的变化
    ycol = 'ln_patents_plus_1' if data_type == 'patent' else 'ln_citations_plus_1'  
    control_pre = panel_df[(panel_df['treatment'] == 0) & (panel_df['post'] == 0)][ycol].mean()
    control_post = panel_df[(panel_df['treatment'] == 0) & (panel_df['post'] == 1)][ycol].mean()
    control_change = control_post - control_pre
    
    # 处理组在投资前后的变化
    treatment_pre = panel_df[(panel_df['treatment'] == 1) & (panel_df['post'] == 0)][ycol].mean()
    treatment_post = panel_df[(panel_df['treatment'] == 1) & (panel_df['post'] == 1)][ycol].mean()
    treatment_change = treatment_post - treatment_pre
    
    print(f"   - 控制组投资前平均ln(专利+1): {control_pre:.4f}")
    print(f"   - 控制组投资后平均ln(专利+1): {control_post:.4f}")
    print(f"   - 控制组变化: {control_change:.4f}")
    print(f"   - 处理组投资前平均ln(专利+1): {treatment_pre:.4f}")
    print(f"   - 处理组投资后平均ln(专利+1): {treatment_post:.4f}")
    print(f"   - 处理组变化: {treatment_change:.4f}")
    
    if results is None:
        return None
        
    # 6. 保存面板数据和回归结果到输出文件
    print(f"保存面板数据和回归结果到: {output_file}")
    with pd.ExcelWriter(output_file, engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        # 保存面板数据
        panel_df.to_excel(writer, sheet_name='面板数据', index=False)
        print(f"   - 面板数据已保存到'面板数据'工作表")
        
        # 保存回归结果摘要
        results_summary = pd.DataFrame({
            '变量': results.params.index,
            '系数': results.params.values,
            '标准误': results.std_errors.values,
            't值': results.tstats.values,
            'p值': results.pvalues.values,
            '置信区间下限': results.conf_int().iloc[:, 0].values,
            '置信区间上限': results.conf_int().iloc[:, 1].values
        })
        results_summary.to_excel(writer, sheet_name='回归结果', index=False)
        print(f"   - 回归结果已保存到'回归结果'工作表")
        
        # 保存回归统计信息
        stats_data = {
            '统计指标': [
                'R方', 'F统计量', 'F统计量p值', 
                '观测值数量', '残差自由度', '模型自由度'
            ],
        }
        
        # 尝试获取R方等统计量，逐个处理以避免单个字段不可用导致全部失败
        stats_values = []
        
        # R方
        try:
            stats_values.append(results.rsquared)
        except AttributeError:
            stats_values.append(np.nan)
        
        # F统计量
        try:
            stats_values.append(results.f_statistic.stat)
        except AttributeError:
            stats_values.append(np.nan)
        
        # F统计量p值
        try:
            stats_values.append(results.f_statistic.pval)
        except AttributeError:
            stats_values.append(np.nan)
        
        # 观测值数量
        try:
            stats_values.append(results.nobs)
        except AttributeError:
            stats_values.append(np.nan)
        
        # 残差自由度
        try:
            stats_values.append(results.df_resid)
        except AttributeError:
            stats_values.append(np.nan)
        
        # 模型自由度
        try:
            stats_values.append(results.df_model)
        except AttributeError:
            stats_values.append(np.nan)
        
        stats_data['数值'] = stats_values
        
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='回归统计', index=False)
        print(f"   - 回归统计已保存到'回归统计'工作表")
        
        # 保存省份虚拟变量信息
        if province_dummy:
            province_info = pd.DataFrame({
                '省份虚拟变量': province_cols       ,
                '系数': [results.params.get(col, np.nan) for col in province_cols],
                't值': [results.tstats.get(col, np.nan) for col in province_cols],
                'p值': [results.pvalues.get(col, np.nan) for col in province_cols],
                '显著性': ['显著' if results.pvalues.get(col, 1) < 0.05 else '不显著' for col in province_cols]
            })
            province_info.to_excel(writer, sheet_name='省份虚拟变量', index=False)
            print(f"   - 省份虚拟变量信息已保存到'省份虚拟变量'工作表")
    
    print(f"✅ 所有数据已成功保存到: {output_file}")
    
    return {
        'panel_df': panel_df,
        'regression_results': results,
        'did_effect': results.params['treatment_post'],
        'did_t_value': results.tstats['treatment_post'],
        'did_p_value': results.pvalues['treatment_post'],
    }

def add_urban_col(df):
    from growth_regress import read_urban
    urban_df = read_urban() 
    urban_rates =[]
    for idx, row in df.iterrows():
        province ,year = row['省份'],row['year']
        try:
            if year == 2024:
                year = 2023
            urban_rates.append(urban_df.loc[province, str(year)])
        except Exception as e:
            print(f"  错误: 处理{province}{year}数据时发生异常: {e}")

    df['城镇化率'] = pd.Series(urban_rates)/100
    df['ln_城镇化率'] = np.log(df['城镇化率'] + 1)
    return df

def add_fixed_invest_col(df):
    from growth_regress import read_fixed_invest
    investment_df, investment_col = read_fixed_invest()
    investment_values =[]
    for idx, row in df.iterrows():
        province ,year= row['省份'],row['year']
        if year == 2024:
            year = 2023
        investment_values.append(investment_df.loc[year,province][investment_col])
    df['固定资产投资'] = pd.Series(investment_values)
    df['ln_固定资产投资'] = np.log(df['固定资产投资'] + 1)
    return df

def add_industry_col(df):
    # 第二产业产值占比
    gdp_df = pd.read_excel('gdp.xlsx', sheet_name='sheet1',index_col=[0,1])
    industry_values =[]
    for idx, row in df.iterrows():
        province ,year= row['省份'],row['year']
        industry_values.append(gdp_df.loc[year,province]['第二产业占GDP的比重(%)'])
    df['二产比例'] = pd.Series(industry_values)
    return df

def add_employment_col(df):
    # 第二产业从业人口占比
    employment_df = pd.read_excel('就业人口.xlsx',index_col=[1,2]) #年份，省份
    employment_values =[]
    for idx, row in df.iterrows():
        province ,year= row['省份'],row['year']
        if year == 2024:
            year = 2023
        employment_values.append(employment_df.loc[year,province]['第二产业就业人员比例(%)'])
    df['二产就业比例'] = pd.Series(employment_values)
    return df

def add_lagged_patent_col(df):
    df['lagged_patent_count'] = df['ln_patents_plus_1'].shift(1)
    df.dropna(inplace=True)
    return df

def perform_did_regression(data_type):

    try:
        choice = input("\n请输入选择: (1增加解释变量 2回归): ").strip()

        if choice == '1': 
            # 2. 准备面板数据
            panel_df = read_panel_data(data_type)
            # panel_df = prepare_panel_data(data_type)
            
            # panel_df = add_urban_col(panel_df)
            # panel_df = add_fixed_invest_col(panel_df)

            
            # panel_df = add_industry_col(panel_df)
            # panel_df = add_employment_col(panel_df)
            # panel_df = _generate_dummy_variables(data_type, panel_df)
            panel_df = add_lagged_patent_col(panel_df)
            
            write_panel_data(data_type, panel_df)
            
        elif choice == '2':
            _perform_regression(data_type, province_dummy=True, stage_dummy=True)
        
    except Exception as e:
        print(f"执行带年份虚拟变量的DID回归时出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None



def read_panel_data(data_type)->pd.DataFrame:
    if data_type == 'patent':
        return pd.read_excel('patent_analysis/did_panel_data_patents.xlsx', sheet_name='面板数据')
    elif data_type == 'citation':
        return pd.read_excel('patent_analysis/did_panel_data_patents.xlsx', sheet_name='面板数据')

def write_panel_data(data_type, panel_df):
    if data_type == 'patent':
        panel_df.to_excel('patent_analysis/did_panel_data_patents.xlsx', sheet_name='面板数据', index=False)
    elif data_type == 'citation':
        panel_df.to_excel('patent_analysis/did_panel_data_patents.xlsx', sheet_name='面板数据', index=False)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='DID回归分析')
    parser.add_argument('--data_type', 
                       choices=['patent', 'citation'], 
                       default='patent',
                       help='数据类型：patent(专利数量) 或 citation(被引证次数)')
    parser.add_argument('--province_dummy', 
                       type=lambda x: x.lower() == 'true',
                       default=True,
                       help='是否启用省份虚拟变量')
    parser.add_argument('--stage_dummy', 
                       type=lambda x: x.lower() == 'true',
                       default=True,
                       help='是否启用投资阶段虚拟变量')
    parser.add_argument('--add_gdp', 
                       type=lambda x: x.lower() == 'true',
                       default=True,
                       help='是否添加GDP控制变量')
    parser.add_argument('--add_urban', 
                       type=lambda x: x.lower() == 'true',
                       default=True,
                       help='是否添加城镇化率控制变量')
    parser.add_argument('--add_fixed_invest', 
                       type=lambda x: x.lower() == 'true',
                       default=True,
                       help='是否添加固定资产投资控制变量')
    parser.add_argument('--add_industry', 
                       type=lambda x: x.lower() == 'true',
                       default=True,
                       help='是否添加第二产业比例控制变量')
    parser.add_argument('--add_employment', 
                       type=lambda x: x.lower() == 'true',
                       default=True,
                       help='是否添加第二产业就业比例控制变量')
    
    args = parser.parse_args()
    
    print(f"=== DID回归分析 - {args.data_type} ===")
    print(f"省份虚拟变量: {args.province_dummy}")
    print(f"投资阶段虚拟变量: {args.stage_dummy}")
    print(f"GDP控制变量: {args.add_gdp}")
    print(f"城镇化率控制变量: {args.add_urban}")
    print(f"固定资产投资控制变量: {args.add_fixed_invest}")
    print(f"第二产业比例控制变量: {args.add_industry}")
    print(f"第二产业就业比例控制变量: {args.add_employment}")
    
    # 执行DID回归分析
    result = perform_did_regression(data_type=args.data_type)
