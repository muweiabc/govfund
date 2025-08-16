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

filter_data() 

def perform_did_regression_with_year_dummies(enable_province_dummies=True, use_time_effects=True):
    """
    根据patent_investment_timeline_with_province_gdp数据做DID回归
    被解释变量是公司某年的ln(专利数+1)
    treatment是是否接受政府引导基金投资
    post变量在投资后3年取1，投资前3年取0
    控制变量包括公司所在省份当年ln(GDP+1)和年份虚拟变量
    
    参数:
    enable_province_dummies: 是否启用省份虚拟变量，默认True
    enable_time_dummies: 是否启用年份虚拟变量，默认True
    """
    try:
        print("=== 执行带年份虚拟变量的DID回归分析 ===")
        
        # 1. 读取带GDP数据的timeline数据
        print("1. 读取带GDP数据的timeline数据...")
        df = pd.read_excel('regress_data_with_gdp.xlsx', sheet_name='回归数据')
        print(f"   - 数据行数: {len(df):,}")
        
        # 2. 创建面板数据结构
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
                        'ln_patent_plus_1': np.log(patent_count + 1),
                        'province': province,
                        'gdp': gdp_value,
                        'ln_gdp': ln_gdp,
                        'time_to_investment': year_offset,
                        'period': 'pre'
                    })
            
            # # 投资当年数据 (post=0)
            # patent_count = row['投资当年专利数']
            # gdp_value = row['投资当年GDP']
            # ln_gdp = row['ln_投资当年GDP']
            
            # panel_data.append({
            #     'company': company,
            #     'year': investment_year,
            #     'investment_year': investment_year,
            #     'treatment': treatment,
            #     'post': 0,  # 投资当年也算投资前
            #     'patent_count': patent_count,
            #     'ln_patent_plus_1': np.log(patent_count + 1),
            #     'province': province,
            #     'gdp': gdp_value,
            #     'ln_gdp': ln_gdp,
            #     'time_to_investment': 0,
            #     'period': 'investment_year'
            # })
            
            # 后3年数据 (post=1)
            for year_offset in range(1, 4):
                year = investment_year + year_offset
                if year <= 2025:  # 确保年份在专利数据范围内
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
                        'ln_patent_plus_1': np.log(patent_count + 1),
                        'province': province,
                        'gdp': gdp_value,
                        'ln_gdp': ln_gdp,
                        'time_to_investment': -year_offset,
                        'period': 'post'
                    })
        
        # 3. 创建面板数据框
        print("3. 创建面板数据框...")
        panel_df = pd.DataFrame(panel_data)
        print(f"   - 面板数据行数: {len(panel_df):,}")
        print(f"   - 面板数据列数: {len(panel_df.columns)}")
        
        
        # 5. 数据统计
        print("5. 面板数据统计...")
        print(f"   - 公司数量: {panel_df['company'].nunique():,}")
        print(f"   - 年份范围: {panel_df['year'].min()} - {panel_df['year'].max()}")
        print(f"   - 投资年份范围: {panel_df['investment_year'].min()} - {panel_df['investment_year'].max()}")
        
        # 按treatment和post分组统计
        group_stats = panel_df.groupby(['treatment', 'post'])['ln_patent_plus_1'].agg(['count', 'mean', 'std']).round(4)
        print(f"\n6. 分组统计:")
        print(group_stats)
        
        # 7. 执行DID回归（带GDP控制变量和年份虚拟变量）
        print("\n7. 执行带年份虚拟变量的DID回归...")
        
        try:
            from linearmodels import PanelOLS
            
            # 设置面板数据索引
            panel_df = panel_df.set_index(['company', 'year'])
            
            # 添加交互项
            panel_df['treatment_post'] = panel_df['treatment'] * panel_df['post']
            
            # 创建省份虚拟变量（如果启用）
            province_dummy_cols = []
            if enable_province_dummies:
                print("   - 创建省份虚拟变量...")
                provinces = panel_df['province'].unique()
                base_province = provinces[0]
                print(f"   - 基准省份: {base_province}")
                
                for province in provinces[1:]:
                    panel_df[f'province_{province}'] = (panel_df['province'] == province).astype(int)
                
                province_dummy_cols = [col for col in panel_df.columns if col.startswith('province_')]
                print(f"   - 省份虚拟变量数量: {len(province_dummy_cols)}")
            else:
                print("   - 省份虚拟变量已禁用")
            
            # 准备回归变量
            control_vars = ['treatment','treatment_post', 'ln_gdp'] 
            # control_vars = ['treatment', 'post', 'treatment_post','ln_gdp'] 

            if enable_province_dummies:
                control_vars += province_dummy_cols 
            X = panel_df[control_vars]
            y = panel_df['ln_patent_plus_1']
            
            print(f"   - 回归变量数量: {len(control_vars)}")
            control_desc = "GDP"
        
            if enable_province_dummies:
                control_desc = f"{len(province_dummy_cols)} 个省份虚拟变量 + " + control_desc
            print(f"   - 控制变量: {control_desc}")
            
            # df.index.get_level_values('year') 获取所有时间值

            # 执行PanelOLS回归
            model = PanelOLS(y, X, entity_effects=False, time_effects=True)
            results = model.fit(cov_type='clustered', cluster_entity=True)
            
            print("   - 回归完成")
            print(f"   - 样本数: {len(panel_df):,}")
            print(f"   - 公司数: {panel_df.index.get_level_values('company').nunique():,}")
            
            # 8. 显示回归结果
            print("\n8. 回归结果:")
            print("=" * 80)
            print(results)
            print("=" * 80)
            
            # 9. 关键系数解释
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
                print(f"\n11. 省份虚拟变量显著性:")
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
                print(f"\n11. 省份虚拟变量显著性: 已禁用")
            
            # 12. 计算边际效应
            print(f"\n12. 边际效应分析:")
            # 控制组在投资前后的变化
            control_pre = panel_df[(panel_df['treatment'] == 0) & (panel_df['post'] == 0)]['ln_patent_plus_1'].mean()
            control_post = panel_df[(panel_df['treatment'] == 0) & (panel_df['post'] == 1)]['ln_patent_plus_1'].mean()
            control_change = control_post - control_pre
            
            # 处理组在投资前后的变化
            treatment_pre = panel_df[(panel_df['treatment'] == 1) & (panel_df['post'] == 0)]['ln_patent_plus_1'].mean()
            treatment_post = panel_df[(panel_df['treatment'] == 1) & (panel_df['post'] == 1)]['ln_patent_plus_1'].mean()
            treatment_change = treatment_post - treatment_pre
            
            print(f"   - 控制组投资前平均ln(专利+1): {control_pre:.4f}")
            print(f"   - 控制组投资后平均ln(专利+1): {control_post:.4f}")
            print(f"   - 控制组变化: {control_change:.4f}")
            print(f"   - 处理组投资前平均ln(专利+1): {treatment_pre:.4f}")
            print(f"   - 处理组投资后平均ln(专利+1): {treatment_post:.4f}")
            print(f"   - 处理组变化: {treatment_change:.4f}")
            print(f"   - DID效应 (处理组变化 - 控制组变化): {treatment_change - control_change:.4f}")
            
            # 13. 保存结果
            # print("\n13. 保存结果...")
            
            # # 保存面板数据
            # panel_filename = 'did_panel_data_with_year_dummies.xlsx'
            # with pd.ExcelWriter(panel_filename, engine='openpyxl') as writer:
            #     panel_df.reset_index().to_excel(writer, sheet_name='面板数据', index=False)
                
            #     # 保存回归结果
            #     # variables = ['Treatment', 'Post', 'Treatment×Post', 'ln(GDP+1)']
            #     # coefficients = [results.params['treatment'], results.params['post'], 
            #     #               results.params['treatment_post'], results.params['ln_gdp']]
            #     # std_errors = [results.std_errors['treatment'], results.std_errors['post'], 
            #     #              results.std_errors['treatment_post'], results.std_errors['ln_gdp']]
            #     # t_stats = [results.tstats['treatment'], results.tstats['post'], 
            #     #           results.tstats['treatment_post'], results.tstats['ln_gdp']]
            #     # p_values = [results.pvalues['treatment'], results.pvalues['post'], 
            #     #            results.pvalues['treatment_post'], results.pvalues['ln_gdp']]
                
                
            #     if enable_province_dummies:
            #         variables += [f'省份{col.replace("province_", "")}' for col in province_dummy_cols]
            #         coefficients += [results.params[col] for col in province_dummy_cols]
            #         std_errors += [results.std_errors[col] for col in province_dummy_cols]
            #         t_stats += [results.tstats[col] for col in province_dummy_cols]
            #         p_values += [results.pvalues[col] for col in province_dummy_cols]
                
            #     results_summary = pd.DataFrame({
            #         '变量': variables,
            #         '系数': coefficients,
            #         '标准误': std_errors,
            #         't值': t_stats,
            #         'p值': p_values
            #     })
            #     results_summary.to_excel(writer, sheet_name='回归结果', index=False)
                
            #     # 保存分组统计
            #     group_stats.to_excel(writer, sheet_name='分组统计')
                
            #     # 保存GDP统计
            #     gdp_stats = panel_df[['gdp', 'ln_gdp']].describe()
            #     gdp_stats.to_excel(writer, sheet_name='GDP统计')
            
                
            #     # 保存省份虚拟变量统计（如果启用）
            #     if enable_province_dummies:
            #         province_dummy_stats = panel_df[province_dummy_cols].describe()
            #         province_dummy_stats.to_excel(writer, sheet_name='省份虚拟变量统计')
            
            # print(f"   - 面板数据已保存: {panel_filename}")
            
            return {
                'panel_df': panel_df,
                'regression_results': results,
                'did_effect': results.params['treatment_post'],
                'did_t_value': results.tstats['treatment_post'],
                'did_p_value': results.pvalues['treatment_post'],
                'gdp_effect': results.params['ln_gdp'],
                'province_dummy_count': len(province_dummy_cols) if enable_province_dummies else 0,
                'significant_province_dummies': len(significant_province_dummies),
                
            }
            
        except ImportError:
            print("   错误: 需要安装linearmodels库")
            print("   请运行: pip install linearmodels")
            return None
        
    except Exception as e:
        print(f"执行带年份虚拟变量的DID回归时出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 执行带年份虚拟变量的DID回归分析
    # 可以通过参数控制是否启用省份虚拟变量和时间虚拟变量
    result = perform_did_regression_with_year_dummies(
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