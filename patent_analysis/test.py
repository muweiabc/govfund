import pandas as pd
import numpy as np
from linearmodels import PanelOLS
from linearmodels.panel import PanelOLS
import statsmodels.api as sm
from scipy import stats

# =========================================================================
# 1. 模拟面板数据 (请替换为您的实际数据)
# =========================================================================
np.random.seed(42)
num_entities = 30
num_times = 11  # 2015-2025
total_obs = num_entities * num_times

entities = np.array([f'firm_{i}' for i in range(num_entities)])
times = np.array([(2015 + i) for i in range(num_times)])

data = pd.DataFrame({
    'PGDP': np.random.rand(total_obs) * 100,
    'GVC': np.random.rand(total_obs) * 5 + 1.5,
    'RO': np.random.rand(total_obs) * 20 + 5,
    'IFA': np.random.rand(total_obs) * 1 + 0.1,
    'DI': np.random.rand(total_obs) * 10 - 5,
    'UL': np.random.rand(total_obs) * 15 + 8,
    'FIL': np.random.rand(total_obs) * 1 - 0.5,
    'FDL': np.random.rand(total_obs) * 0.5,
    'RL': np.random.rand(total_obs) * 2 - 0.5,
    'entity': np.tile(entities, num_times),
    'time': np.repeat(times, num_entities)
})

# 创建 PanelData 对象
data = data.set_index(['entity', 'time'])
pgdp = data['PGDP']
exog = data[['GVC', 'RO', 'IFA', 'DI', 'UL', 'FIL', 'FDL', 'RL']]

# =========================================================================
# 2. 运行多个回归模型
# =========================================================================
# 注意：这里我们使用'between' estimator来简化，因为PanelOLS默认是'within'
# 如果您需要固定效应模型，请使用 `entity_effects=True`
# 为了复现表格中的多列，我们每次运行都使用不同的自变量组合

# Model 1
mod1 = PanelOLS(pgdp, exog[['GVC', 'RO', 'IFA', 'DI', 'UL', 'FIL', 'FDL', 'RL']], entity_effects=True)
res1 = mod1.fit(cov_type='robust')

# Model 2
mod2 = PanelOLS(pgdp, exog[['GVC', 'RO', 'IFA', 'DI', 'UL', 'FIL', 'FDL']], entity_effects=True)
res2 = mod2.fit(cov_type='robust')

# Model 3
mod3 = PanelOLS(pgdp, exog[['GVC', 'RO', 'IFA', 'DI', 'UL', 'FIL']], entity_effects=True)
res3 = mod3.fit(cov_type='robust')

# Model 4
mod4 = PanelOLS(pgdp, exog[['GVC', 'RO', 'IFA', 'DI', 'UL']], entity_effects=True)
res4 = mod4.fit(cov_type='robust')

# Model 5
mod5 = PanelOLS(pgdp, exog[['GVC', 'RO', 'IFA', 'DI']], entity_effects=True)
res5 = mod5.fit(cov_type='robust')

# Model 6
mod6 = PanelOLS(pgdp, exog[['GVC', 'RO', 'IFA']], entity_effects=True)
res6 = mod6.fit(cov_type='robust')

# Model 7
mod7 = PanelOLS(pgdp, exog[['GVC', 'RO']], entity_effects=True)
res7 = mod7.fit(cov_type='robust')

# Model 8
mod8 = PanelOLS(pgdp, exog[['GVC']], entity_effects=True)
res8 = mod8.fit(cov_type='robust')


# =========================================================================
# 3. 手动创建结果表格（因为linearmodels与statsmodels的兼容性问题）
# =========================================================================
results_list = [res1, res2, res3, res4, res5, res6, res7, res8]
model_names = [f'({i})' for i in range(1, 9)]

# 创建结果表格                        【
def create_results_table(results_list, model_names):
    """手动创建结果表格"""
    all_vars = set()
    for res in results_list:
        all_vars.update(res.params.index)
    
    # 按照图片中的顺序排列变量
    regressor_order = ['GVC', 'RO', 'IFA', 'DI', 'UL', 'FIL', 'FDL', 'RL', 'const']
    ordered_vars = [var for var in regressor_order if var in all_vars]
    
    # 创建结果DataFrame
    results_data = []
    for i, (res, model_name) in enumerate(zip(results_list, model_names)):
        for var in ordered_vars:
            if var in res.params.index:
                coef = res.params[var]
                try:
                    se = res.std_errors[var]
                except AttributeError:
                    se = np.sqrt(res.cov.loc[var, var])
                t_stat = coef / se
                p_val = 2 * (1 - stats.t.cdf(abs(t_stat), res.df_resid))
                
                results_data.append({
                    'Model': model_name,
                    'Variable': var,
                    'Coefficient': coef,
                    'Std_Error': se,
                    'T_Statistic': t_stat,
                    'P_Value': p_val
                })
            else:
                results_data.append({
                    'Model': model_name,
                    'Variable': var,
                    'Coefficient': np.nan,
                    'Std_Error': np.nan,
                    'T_Statistic': np.nan,
                    'P_Value': np.nan
                })
    
    return pd.DataFrame(results_data)

# 生成表格
results_df = create_results_table(results_list, model_names)

# 创建格式化的表格
def format_table(df):
    """格式化表格输出"""
    print("表 4.4 基础回归结果")
    print("=" * 80)
    
    # 按模型分组显示
    for model in df['Model'].unique():
        model_data = df[df['Model'] == model]
        print(f"\n{model}:")
        print("-" * 40)
        for _, row in model_data.iterrows():
            if not pd.isna(row['Coefficient']):
                coef = row['Coefficient']
                se = row['Std_Error']
                t_stat = row['T_Statistic']
                p_val = row['P_Value']
                
                # 添加显著性标记
                if p_val < 0.01:
                    sig = "***"
                elif p_val < 0.05:
                    sig = "**"
                elif p_val < 0.1:
                    sig = "*"
                else:
                    sig = ""
                
                print(f"{row['Variable']:12} {coef:8.3f}{sig:3} ({se:.3f})")
            else:
                print(f"{row['Variable']:12} {'':8}    {'':8}")
    
    print("\n注: 括号内为标准误，*** p<0.01, ** p<0.05, * p<0.1")
    print("=" * 80)

table = format_table(results_df)

# =========================================================================
# 4. 保存结果
# =========================================================================
# 保存结果到CSV文件
results_df.to_csv("regression_results.csv", index=False)
print("\n结果已保存到 regression_results.csv")

# 保存为Excel文件
with pd.ExcelWriter("regression_results.xlsx", engine='openpyxl') as writer:
    results_df.to_excel(writer, sheet_name='回归结果', index=False)
    
    # 创建汇总统计
    summary_stats = []
    for i, res in enumerate(results_list):
        summary_stats.append({
            'Model': f'({i+1})',
            'N': int(res.nobs),
            'R_squared': res.rsquared,
            'F_statistic': res.f_statistic.stat if hasattr(res, 'f_statistic') else np.nan,
            'F_pvalue': res.f_statistic.pval if hasattr(res, 'f_statistic') else np.nan
        })
    
    summary_df = pd.DataFrame(summary_stats)
    summary_df.to_excel(writer, sheet_name='模型统计', index=False)

print("结果已保存到 regression_results.xlsx")