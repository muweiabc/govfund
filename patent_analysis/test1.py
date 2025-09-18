import pandas as pd
import numpy as np
from linearmodels import PanelOLS
from statsmodels.iolib.summary2 import summary_col

# =========================================================================
# 1. 模拟面板数据
# =========================================================================
np.random.seed(42)
num_entities = 30
num_times = 11
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
data = data.set_index(['entity', 'time'])
pgdp = data['PGDP']
exog = data[['GVC', 'RO', 'IFA', 'DI', 'UL', 'FIL', 'FDL', 'RL']]

# =========================================================================
# 2. 编写一个兼容 statsmodels 的包装类 (修正 conf_int 方法)
# =========================================================================
class LinearmodelsResultsWrapper:
    """
    一个简单的类，用于将 linearmodels 的结果对象包装成 statsmodels summary_col 
    函数所需的格式。
    """
    def __init__(self, lm_results):
        self.params = lm_results.params
        self.pvalues = lm_results.pvalues
        self.tvalues = lm_results.tstats
        self.bse = lm_results.std_errors
        self.rsquared = lm_results.rsquared
        self.nobs = lm_results.nobs
        self.model = self
        self.exog_names = list(self.params.index)
        self.endog_names = lm_results.model.dependent.dataframe.columns[0]
        self._lm_results = lm_results

    def conf_int(self, alpha=0.05):
        """代理原始 linearmodels 结果对象的 conf_int 方法。"""
        # This will work for recent linearmodels versions that accept 'alpha'
        try:
            return self._lm_results.conf_int(level=1 - alpha)
        # This will work for older linearmodels versions that do not accept 'alpha'
        except TypeError:
            return self._lm_results.conf_int()


# =========================================================================
# 3. 运行多个回归模型并包装结果
# =========================================================================
results_list = []
exog_cols_list = [
    ['GVC', 'RO', 'IFA', 'DI', 'UL', 'FIL', 'FDL', 'RL'],
    ['GVC', 'RO', 'IFA', 'DI', 'UL', 'FIL', 'FDL'],
    ['GVC', 'RO', 'IFA', 'DI', 'UL', 'FIL'],
    ['GVC', 'RO', 'IFA', 'DI', 'UL'],
    ['GVC', 'RO', 'IFA', 'DI'],
    ['GVC', 'RO', 'IFA'],
    ['GVC', 'RO'],
    ['GVC']
]

for exog_cols in exog_cols_list:
    mod = PanelOLS(pgdp, exog[exog_cols], entity_effects=True)
    res = mod.fit(cov_type='robust')
    results_list.append(LinearmodelsResultsWrapper(res))

# =========================================================================
# 4. 使用 summary_col 合并结果并格式化
# =========================================================================
model_names = [f'({i})' for i in range(1, 9)]

info_dict = {
    'N': lambda x: f'{int(x.nobs)}',
    'R-sq': lambda x: f'{x.rsquared:.4f}'
}

regressor_order = ['GVC', 'RO', 'IFA', 'DI', 'UL', 'FIL', 'FDL', 'RL', 'const']

table = summary_col(
    results=results_list,
    model_names=model_names,
    info_dict=info_dict,
    float_format='%0.3f',
    regressor_order=regressor_order,
    stars=True
)

# =========================================================================
# 5. 打印最终结果
# =========================================================================
print("表 4.4 基础回归结果")
print(table)

with open("regression_results.html", "w") as f:
    f.write(table.as_html())

with open("regression_results.tex", "w") as f:
    f.write(table.as_latex())