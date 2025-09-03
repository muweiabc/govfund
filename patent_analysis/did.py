import pandas as pd
import numpy as np

def filter_data():
    provinces = set(['上海市', '天津市', '江苏省', '浙江省', '广东省', '重庆市', '北京市', '福建省', '河北省',
       '湖北省', '海南省', '山东省', '吉林省', '河南省', '辽宁省', '安徽省', '四川省', '湖南省',
       '江西省', '陕西省', '云南省', '甘肃省', '贵州省', '山西省', '黑龙江省','宁夏', '广西',
       '新疆', '内蒙古', '青海省'])
    df = pd.read_excel('regress_data_with_gdp.xlsx', sheet_name='回归数据')
    df = df[df['省份'].isin(provinces)]
    with pd.ExcelWriter('regress_data_with_gdp.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='回归数据')


def prepare_panel_data(data_type, df):
    """
    准备面板数据结构
    
    参数:
    df: 包含投资和专利数据的DataFrame
    
    返回:
    panel_df: 面板数据DataFrame
    """
    print("2. 创建面板数据结构...")
    
    # 创建前3年和后3年的观测值
    panel_data = []
    
    for idx, row in df.iterrows():
        company = row['公司名称']
        investment_year = row['投资年份']
        treatment = row['treatment']
        province = row['省份']
        
        # 前3年数据 (post=0)
        for year_offset in range(1, 4):
            year = investment_year - year_offset
            if year >= 1992:  # 确保年份在专利数据范围内
                if data_type == 'patent':
                    patent_count = row[f'前3年专利数_前{year_offset}年']
                    gdp_value = row[f'前3年GDP_前{year_offset}年']
                    ln_gdp = row[f'ln_前3年GDP_前{year_offset}年']
                
                    panel_data.append({
                        'company': company,
                        'year': year,
                        'investment_year': investment_year,
                        'treatment': treatment,
                        'post': 0,  # 投资前
                        'patent_count': patent_count,
                        'ln_patents_plus_1': np.log(patent_count + 1),
                        '省份': province,
                        'gdp': gdp_value,
                        'ln_gdp': ln_gdp,
                        'time_to_investment': year_offset,
                        'period': 'pre',
                        '投资阶段':row['投资阶段']
                    })
                else:
                    citations = row[f'前3年被引证数_前{year_offset}年']
                    gdp_value = row[f'前3年GDP_前{year_offset}年']
                    ln_gdp = row[f'ln_前3年GDP_前{year_offset}年']
                    
                    panel_data.append({
                        'company': company,
                        'year': year,
                        'investment_year': investment_year,
                        'treatment': treatment,
                        'post': 0,  # 投资前
                        'citation_count': citations,
                        'ln_citations_plus_1': np.log(citations + 1),
                        '省份': province,
                        'gdp': gdp_value,
                        'ln_gdp': ln_gdp,
                        'time_to_investment': year_offset,
                        'period': 'pre',
                        '投资阶段':row['投资阶段']
                    })
        
        # 后3年数据 (post=1)
        for year_offset in range(1, 4):
            year = investment_year + year_offset
            if year <= 2025:  # 确保年份在专利数据范围内
                if data_type == 'patent':
                    patent_count = row[f'后3年专利数_后{year_offset}年']
                    gdp_value = row[f'后3年GDP_后{year_offset}年']
                    ln_gdp = row[f'ln_后3年GDP_后{year_offset}年']
                    
                    panel_data.append({
                        'company': company,
                        'year': year,
                        'investment_year': investment_year,
                        'treatment': treatment,
                        'post': 1,  # 投资后
                        'patent_count': patent_count,
                        'ln_patents_plus_1': np.log(patent_count + 1),
                        '省份': province,
                        'gdp': gdp_value,
                        'ln_gdp': ln_gdp,
                        'time_to_investment': -year_offset,
                        'period': 'post',
                        '投资阶段':row['投资阶段']
                    })
                else:
                    citations = row[f'后3年被引证数_后{year_offset}年']
                    gdp_value = row[f'后3年GDP_后{year_offset}年']
                    ln_gdp = row[f'ln_后3年GDP_后{year_offset}年']
                    
                    panel_data.append({
                        'company': company,
                        'year': year,
                        'investment_year': investment_year,
                        'treatment': treatment,
                        'post': 1,  # 投资后
                        'citation_count': citations,
                        'ln_citations_plus_1': np.log(citations + 1),
                        '省份': province,
                        'gdp': gdp_value,
                        'ln_gdp': ln_gdp,
                        'time_to_investment': -year_offset,
                        'period': 'post',
                        '投资阶段':row['投资阶段']
                    })
    
    # 创建面板数据框
    print("3. 创建面板数据框...")
    panel_df = pd.DataFrame(panel_data)
    print(f"   - 面板数据行数: {len(panel_df):,}")
    print(f"   - 面板数据列数: {len(panel_df.columns)}")
    
    # 数据统计
    print("4. 面板数据统计...")
    print(f"   - 公司数量: {panel_df['company'].nunique():,}")
    print(f"   - 年份范围: {panel_df['year'].min()} - {panel_df['year'].max()}")
    print(f"   - 投资年份范围: {panel_df['investment_year'].min()} - {panel_df['investment_year'].max()}")
    
    # 按treatment和post分组统计
    if data_type == 'patent':
        group_stats = panel_df.groupby(['treatment', 'post'])['ln_patents_plus_1'].agg(['count', 'mean', 'std']).round(4)
    else:
        group_stats = panel_df.groupby(['treatment', 'post'])['ln_citations_plus_1'].agg(['count', 'mean', 'std']).round(4)
    print(f"\n5. 分组统计:")
    print(group_stats)
    
    return panel_df


def generate_dummy_variables(panel_df, enable_province_dummies=True, enable_stage_dummies=True):
    """
    生成虚拟变量
    
    参数:
    panel_df: 面板数据DataFrame
    enable_province_dummies: 是否启用省份虚拟变量
    
    返回:
    panel_df: 添加了虚拟变量的DataFrame
    province_dummy_cols: 省份虚拟变量列名列表
    """
    print("6. 生成虚拟变量...")
    
    # 设置面板数据索引
    panel_df = panel_df.set_index(['company', 'year'])
    
    # 添加交互项
    panel_df['treatment_post'] = panel_df['treatment'] * panel_df['post']
    
    # 创建省份虚拟变量（如果启用）
    if enable_province_dummies:
        print("   - 创建省份虚拟变量...")
        provinces = panel_df['省份'].unique()
        base_province = provinces[0]
        print(f"   - 基准省份: {base_province}")
        
        # 使用pd.get_dummies创建省份虚拟变量
        panel_dummies = pd.get_dummies(panel_df, columns=['省份','投资阶段'], prefix=['省','投资阶段'], drop_first=True)
        
        
    else:
        print("   - 省份虚拟变量已禁用")
    
    return panel_dummies


def perform_regression(data_type, panel_df, province_dummy_cols, enable_province_dummies=True):
    """
    执行DID回归分析
    
    参数:
    panel_df: 面板数据DataFrame
    province_dummy_cols: 省份虚拟变量列名列表
    enable_province_dummies: 是否启用省份虚拟变量
    
    返回:
    results: 回归结果
    significant_province_dummies: 显著的省份虚拟变量列表
    """
    print("7. 执行带年份虚拟变量的DID回归...")
    
    try:
        from linearmodels import PanelOLS
        
        # 准备回归变量
        control_vars = ['treatment','treatment_post', 'ln_gdp']
        
        # if enable_province_dummies:
        #     control_vars += province_dummy_cols
        
        X = panel_df[control_vars]
        if data_type == 'patent':
            y = panel_df['ln_patents_plus_1']
        else:
            y = panel_df['ln_citations_plus_1']
        
        print(f"   - 回归变量数量: {len(control_vars)}")
        control_desc = "GDP"
        
        if enable_province_dummies:
            control_desc = f"{len(province_dummy_cols)} 个省份虚拟变量 + " + control_desc
        print(f"   - 控制变量: {control_desc}")
        
        # 执行PanelOLS回归
        model = PanelOLS(y, X, entity_effects=False, time_effects=True)
        results = model.fit(cov_type='clustered', cluster_entity=True)
        
        print("   - 回归完成")
        print(f"   - 样本数: {len(panel_df):,}")
        print(f"   - 公司数: {panel_df.index.get_level_values('company').nunique():,}")
        
        # 显示回归结果
        print("\n8. 回归结果:")
        print("=" * 80)
        print(results)
        print("=" * 80)
        
        # 关键系数解释
        print("\n9. 关键系数解释:")
        if 'treatment' in results.params.index:
            print(f"   - Treatment效应 (β1): {results.params['treatment']:.4f}")
        if 'post' in results.params.index:
            print(f"   - Post效应 (β2): {results.params['post']:.4f}")
        print(f"   - DID效应 (β3): {results.params['treatment_post']:.4f}")
        print(f"   - GDP控制变量 (β4): {results.params['ln_gdp']:.4f}")
        print(f"   - DID效应t值: {results.tstats['treatment_post']:.4f}")
        print(f"   - DID效应p值: {results.pvalues['treatment_post']:.4f}")
        
        # 显示省份虚拟变量的显著性（如果启用）
        significant_province_dummies = []
        if enable_province_dummies:
            print(f"\n10. 省份虚拟变量显著性:")
            for col in province_dummy_cols:
                if col in results.params.index:
                    p_value = results.pvalues[col]
                    if p_value < 0.05:
                        significant_province_dummies.append((col, results.params[col], p_value))
            
            if significant_province_dummies:
                print(f"   - 显著的省份虚拟变量 (p<0.05): {len(significant_province_dummies)} 个")
                print(f"   - 显示前10个显著的省份虚拟变量:")
                for dummy, coef, p_val in significant_province_dummies[:10]:
                    province_name = dummy.replace('province_', '')
                    print(f"     {province_name}: 系数={coef:.4f}, p值={p_val:.4f}")
            else:
                print("   - 没有显著的省份虚拟变量")
        else:
            print(f"\n10. 省份虚拟变量显著性: 已禁用")
        
        # 计算边际效应
        print(f"\n11. 边际效应分析:")
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
        
        
        return results, significant_province_dummies
        
    except ImportError as e:
        print(e)
        print("   错误: 需要安装linearmodels库")
        return None, []


def perform_did_regression(data_type, input_file, output_file=None, enable_province_dummies=True, use_time_effects=True):
    """
    根据patent_investment_timeline_with_province_gdp数据做DID回归
    被解释变量是公司某年的ln(专利数+1)
    treatment是是否接受政府引导基金投资
    post变量在投资后3年取1，投资前3年取0
    控制变量包括公司所在省份当年ln(GDP+1)和年份虚拟变量
    
    参数:
    input_file: 输入的带GDP数据的文件路径，默认'regress_data_with_gdp.xlsx'
    output_file: 输出文件路径，如果为None则自动生成
    enable_province_dummies: 是否启用省份虚拟变量，默认True
    use_time_effects: 是否启用年份虚拟变量，默认True
    """
    try:
        print("=== 执行带年份虚拟变量的DID回归分析 ===")
        
        # 1. 读取带GDP数据的timeline数据
        print(f"1. 读取带GDP数据的timeline数据: {input_file}...")
        df = pd.read_excel(input_file, sheet_name='回归数据')
        print(f"   - 数据行数: {len(df):,}")
        
        # 2. 准备面板数据
        panel_df = prepare_panel_data(data_type, df)
        
        # 3. 生成虚拟变量
        panel_df = generate_dummy_variables(panel_df, enable_province_dummies)
        
        # 4. 执行回归分析
        results, significant_province_dummies = perform_regression(data_type, panel_df, province_dummy_cols, enable_province_dummies)
        
        if results is None:
            return None
        
        # 5. 生成输出文件名
        if output_file is None:
            # 根据输入文件名自动生成输出文件名
            if 'patent' in input_file.lower():
                output_filename = 'did_panel_data_patents_with_year_dummies.xlsx'
            elif 'citation' in input_file.lower():
                output_filename = 'did_panel_data_citations_with_year_dummies.xlsx'
            else:
                output_filename = 'did_panel_data_with_year_dummies.xlsx'
        else:
            output_filename = output_file
        
        # 6. 保存面板数据和回归结果到输出文件
        print(f"6. 保存面板数据和回归结果到: {output_filename}")
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
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
            
            # 保存DID效应摘要
            did_summary = pd.DataFrame({
                '效应类型': ['DID效应', 'GDP控制变量效应'],
                '系数': [results.params['treatment_post'], results.params['ln_gdp']],
                't值': [results.tstats['treatment_post'], results.tstats['ln_gdp']],
                'p值': [results.pvalues['treatment_post'], results.pvalues['ln_gdp']],
                '显著性': [
                    '显著' if results.pvalues['treatment_post'] < 0.05 else '不显著',
                    '显著' if results.pvalues['ln_gdp'] < 0.05 else '不显著'
                ]
            })
            did_summary.to_excel(writer, sheet_name='DID效应摘要', index=False)
            print(f"   - DID效应摘要已保存到'DID效应摘要'工作表")
            
            # 保存省份虚拟变量信息
            if enable_province_dummies and province_dummy_cols:
                province_info = pd.DataFrame({
                    '省份虚拟变量': province_dummy_cols,
                    '系数': [results.params.get(col, np.nan) for col in province_dummy_cols],
                    't值': [results.tstats.get(col, np.nan) for col in province_dummy_cols],
                    'p值': [results.pvalues.get(col, np.nan) for col in province_dummy_cols],
                    '显著性': ['显著' if results.pvalues.get(col, 1) < 0.05 else '不显著' for col in province_dummy_cols]
                })
                province_info.to_excel(writer, sheet_name='省份虚拟变量', index=False)
                print(f"   - 省份虚拟变量信息已保存到'省份虚拟变量'工作表")
        
        print(f"✅ 所有数据已成功保存到: {output_filename}")
        
        return {
            'panel_df': panel_df,
            'regression_results': results,
            'did_effect': results.params['treatment_post'],
            'did_t_value': results.tstats['treatment_post'],
            'did_p_value': results.pvalues['treatment_post'],
            'gdp_effect': results.params['ln_gdp'],
            'province_dummy_count': len(province_dummy_cols) if enable_province_dummies else 0,
            'significant_province_dummies': len(significant_province_dummies),
            'panel_file': output_filename
        }
        
    except Exception as e:
        print(f"执行带年份虚拟变量的DID回归时出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 执行带年份虚拟变量的DID回归分析
    # 可以通过参数控制是否启用省份虚拟变量和时间虚拟变量
    result = perform_did_regression(
        data_type='patent',
        input_file='patent_analysis/regress_data_patents.xlsx',
        output_file='patent_analysis/did_panel_data_patents.xlsx',
        enable_province_dummies=True,  # 启用省份虚拟变量
        use_time_effects=True       # 启用年份虚拟变量
    )
    
    if result:
        print(f"\n=== 带年份虚拟变量的DID回归分析完成 ===")
        print(f"DID效应系数: {result['did_effect']:.4f}")
        print(f"t值: {result['did_t_value']:.4f}")
        print(f"p值: {result['did_p_value']:.4f}")
        print(f"GDP控制变量系数: {result['gdp_effect']:.4f}")
        print(f"省份虚拟变量数量: {result['province_dummy_count']}")
        print(f"显著的省份虚拟变量: {result['significant_province_dummies']}")
        
        if result['did_p_value'] < 0.05:
            print("✅ DID效应在5%水平上显著")
        elif result['did_p_value'] < 0.1:
            print("⚠️ DID效应在10%水平上显著")
        else:
            print("❌ DID效应不显著")

    else:
        print("回归分析失败")