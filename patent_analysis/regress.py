import pandas as pd
import numpy as np
import sys
import argparse
sys.path.append('.')
from linearmodels import PanelOLS
from statsmodels.iolib.summary2 import summary_col

PATENT_COUNT = 'patent_count'
CITATION_COUNT = 'citation_count'
INVENTION_COUNT = 'invention_count'
INVENTION_CITATION = 'invention_citation'
TREATMENT = 'treatment'
TREATMENT_POST = 'treatment_post'
SECONDARY_EMPLOYMENT_RATIO = '二产就业比例'
LN_GDP = 'lnGDP'
LN_FIXED_INVESTMENT = 'lnFixedInvestment'
URBAN_RATE = '城镇化率'
FIXED_INVESTMENT = '固定资产投资' 

class LinearmodelsResultsWrapper:
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
        try:
            return self._lm_results.conf_int(level=1 - alpha)
        except TypeError:
            return self._lm_results.conf_int()

def read_panel_data(input_file='patent_analysis/regression_panel_data.xlsx'):
    sheet_name = '面板数据'
    return pd.read_excel(input_file, sheet_name=sheet_name)

def main(input_file='patent_analysis/regression_panel_data.xlsx', output_file='patent_analysis/did_results.xlsx'):
    """
    对全部投资进行回归：1依次添加解释变量做稳定性检验；2更改被解释变量，用所有解释变量，做4个回归
    """
    panel_df = read_panel_data(input_file)
    panel_df.set_index(['company', 'year'], inplace=True)
    control_vars = [TREATMENT,TREATMENT_POST,LN_GDP,SECONDARY_EMPLOYMENT_RATIO,URBAN_RATE,LN_FIXED_INVESTMENT]
    describe_vars = control_vars + [PATENT_COUNT,CITATION_COUNT,INVENTION_COUNT,INVENTION_CITATION]
   
    
    # [TREATMENT,TREATMENT_POST,SECONDARY_EMPLOYMENT_RATIO,LN_GDP,URBAN_RATE,FIXED_INVESTMENT]
    province_cols = []
    for col in panel_df.columns:
        if col.startswith('省份'):
            control_vars.append(col)
            province_cols.append(col)
    
    stage_cols = []
    for col in panel_df.columns:
        if col.startswith('投资阶段'):
            control_vars.append(col)
            stage_cols.append(col)

    y_patent = np.log(panel_df[PATENT_COUNT]+1)
    y_citation = np.log(panel_df[CITATION_COUNT]+1)
    y_invention = np.log(panel_df[INVENTION_COUNT]+1)
    y_invention_citation = np.log(panel_df[INVENTION_CITATION]+1)
    panel_df['ln_patent_count_plus_1'] = y_patent
    panel_df['ln_citation_count_plus_1'] = y_citation
    panel_df['ln_invention_count_plus_1'] = y_invention
    panel_df['ln_invention_citation_plus_1'] = y_invention_citation
    describe_vars = describe_vars + ['ln_patent_count_plus_1','ln_citation_count_plus_1','ln_invention_count_plus_1','ln_invention_citation_plus_1']

    stas_x = panel_df[describe_vars].describe(percentiles=[]).T
    
    # stas_y_patent = y_patent.describe()
    # stas_y_citation = y_citation.describe()
    # stas_y_invention = y_invention.describe()
    # stas_y_invention_citation = y_invention_citation.describe()

    # ystats = pd.concat([stas_y_patent, stas_y_citation, stas_y_invention, stas_y_invention_citation], axis=1)
    # ystats.columns = [PATENT_COUNT, CITATION_COUNT, INVENTION_COUNT, INVENTION_CITATION]
    # ystats = ystats.T

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        stas_x.to_excel(writer, sheet_name='回归变量统计')
        # ystats.to_excel(writer, sheet_name='被解释变量统计')   

    results_list = []
    # cols of regression_panel_data.xlsx:
    # treatment	post	treatment_post	year_offset	patent_count  citation_count	invention_count
    #	invention_citation	二产就业比例	GDP	城镇化率	固定资产投资
    exog_cols_list = [
        # ['treatment','treatment_post','二产就业比例','GDP','城镇化率','固定资产投资'] + province_cols + stage_cols,
        [TREATMENT,TREATMENT_POST,SECONDARY_EMPLOYMENT_RATIO,LN_GDP,URBAN_RATE,LN_FIXED_INVESTMENT]+ province_cols + stage_cols,
        [TREATMENT,TREATMENT_POST,SECONDARY_EMPLOYMENT_RATIO,LN_GDP,URBAN_RATE]+ province_cols + stage_cols,
        [TREATMENT,TREATMENT_POST,SECONDARY_EMPLOYMENT_RATIO,LN_GDP]+ province_cols + stage_cols,
        [TREATMENT,TREATMENT_POST,SECONDARY_EMPLOYMENT_RATIO]+ province_cols + stage_cols,
        [TREATMENT,TREATMENT_POST]+ province_cols + stage_cols ,
    ]
    for exog_cols in exog_cols_list:
        result = regress(y_patent,panel_df[exog_cols], output_file, PATENT_COUNT) 
        results_list.append(LinearmodelsResultsWrapper(result))

    # =========================================================================
    # 4. 使用 summary_col 合并结果并格式化 (与之前相同)
    # =========================================================================
    model_names = [f'({i})' for i in range(1, 9)]

    info_dict = {
        'N': lambda x: f'{int(x.nobs)}',
    }

    regressor_order = [TREATMENT_POST, TREATMENT,LN_GDP, SECONDARY_EMPLOYMENT_RATIO,  URBAN_RATE, LN_FIXED_INVESTMENT,'const']

    table = summary_col(
        results=results_list,
        model_names=model_names,
        info_dict=info_dict,
        float_format='%0.3f',
        regressor_order=regressor_order,
        stars=True
    )

    with open('patent_analysis/tex/raw.tex', 'w', encoding='utf-8') as f:
        f.write(table.as_latex())
    print(table.as_text())

    X = panel_df[control_vars]
    regress(y_patent,X, output_file, PATENT_COUNT) 
    regress(y_citation,X, output_file, CITATION_COUNT) 
    regress(y_invention,X, output_file, INVENTION_COUNT) 
    regress(y_invention_citation,X, output_file, INVENTION_CITATION)             # stage_cols.append(col)

def stage_regress(input_file, output_file):
    """按投资时公司发展阶段分组回归
    """
    panel_df = read_panel_data(input_file)
    panel_df.set_index(['company', 'year'], inplace=True)
    control_vars = [TREATMENT,TREATMENT_POST,LN_GDP,SECONDARY_EMPLOYMENT_RATIO,URBAN_RATE,LN_FIXED_INVESTMENT]
        
    # province_cols = []
    # for col in panel_df.columns:
    #     if col.startswith('省份'):
    #         control_vars.append(col)
    #         province_cols.append(col)

    STAGES = ['种子期','初创期','扩张期', '成熟期' ]
    result_list = []
    for stage in STAGES: 
        stage_df = panel_df[panel_df['stage'] == stage]
        y = np.log(stage_df[PATENT_COUNT]+1)
        x = stage_df[control_vars]
        result = regress(y,x,output_file=output_file, sheet_name=stage)
        result_list.append(LinearmodelsResultsWrapper(result))
        # with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        #     stas_x.to_excel(writer, sheet_name='回归变量统计')
    
    model_names = [f'({i})' for i in range(1, len(STAGES)+1)]

    info_dict = {
        'N': lambda x: f'{int(x.nobs)}',
    }

    regressor_order = [TREATMENT_POST, TREATMENT,LN_GDP, SECONDARY_EMPLOYMENT_RATIO,  URBAN_RATE, LN_FIXED_INVESTMENT,'const']

    table = summary_col(
        results=result_list,
        model_names=model_names,
        info_dict=info_dict,
        float_format='%0.3f',
        regressor_order=regressor_order,
        stars=True
    )

    with open('patent_analysis/tex/stage.tex', 'w', encoding='utf-8') as f:
        f.write(table.as_latex())

def region_regress(input_file, output_file):
    """
    按基金和公司省份是否相同分组回归
    """
    panel_df = read_panel_data(input_file)
    panel_df.set_index(['company', 'year'], inplace=True)
    panel_df[LN_GDP] = np.log(panel_df['GDP']+1)
    panel_df[LN_FIXED_INVESTMENT] = np.log(panel_df['固定资产投资']+1)
    control_vars = [TREATMENT,TREATMENT_POST,LN_GDP,URBAN_RATE,LN_FIXED_INVESTMENT]
        
    province_cols = []
    for col in panel_df.columns:
        if col.startswith('省份'):
            province_cols.append(col)
    
    stage_cols = []
    for col in panel_df.columns:
        if col.startswith('投资阶段'):
            stage_cols.append(col)

    SAME_LOCATION = [True, False]
    result_list = []
    for same_location in SAME_LOCATION:
        same_location_df = panel_df
        same_location_df = panel_df[panel_df['same_location'] == same_location]
        y = np.log(same_location_df[CITATION_COUNT]+1)
        x = same_location_df[control_vars + stage_cols]
        
        result = regress(y,x,output_file=output_file, sheet_name=str(same_location))
        result_list.append(LinearmodelsResultsWrapper(result))

def main_lagged(output_file):
    panel_df = read_panel_data()
    panel_df.set_index(['company', 'year'], inplace=True)
   
    control_vars = ['treatment','treatment_post', 'GDP','城镇化率','固定资产投资','二产就业比例']

    panel_df[f'lagged_{PATENT_COUNT}'] = panel_df[PATENT_COUNT].shift(1)
    panel_df[f'lagged_{CITATION_COUNT}'] = panel_df[CITATION_COUNT].shift(1)
    panel_df[f'lagged_{INVENTION_COUNT}'] = panel_df[INVENTION_COUNT].shift(1)
    panel_df[f'lagged_{INVENTION_CITATION}'] = panel_df[INVENTION_CITATION].shift(1)
    panel_df.dropna(inplace=True)

    province_cols = []
    for col in panel_df.columns:
        if col.startswith('省份'):
            control_vars.append(col)
            province_cols.append(col)
    
    stage_cols = []
    for col in panel_df.columns:
        if col.startswith('投资阶段'):
            control_vars.append(col)
            stage_cols.append(col)

    X_patent = panel_df[control_vars+['lagged_'+PATENT_COUNT]]
    y_patent = np.log(panel_df[PATENT_COUNT]+1)
    X_citation = panel_df[control_vars+['lagged_'+CITATION_COUNT]]
    y_citation = np.log(panel_df[CITATION_COUNT]+1)
    X_invention = panel_df[control_vars+['lagged_'+INVENTION_COUNT]]
    y_invention = np.log(panel_df[INVENTION_COUNT]+1)
    X_invention_citation = panel_df[control_vars+['lagged_'+INVENTION_CITATION]]
    y_invention_citation = np.log(panel_df[INVENTION_CITATION]+1)

    stas_x = panel_df.describe()
 
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        stas_x.to_excel(writer, sheet_name='变量统计') 

    regress(y_patent,X_patent, output_file, PATENT_COUNT) 
    regress(y_citation,X_citation, output_file, CITATION_COUNT) 
    regress(y_invention,X_invention, output_file, INVENTION_COUNT) 
    regress(y_invention_citation,X_invention_citation, output_file, INVENTION_CITATION) 

def regress(y, X, output_file,sheet_name):   # 执行PanelOLS回归
    print("执行DID回归...")
    
    model = PanelOLS(y, X, entity_effects=False, time_effects=True)
    results = model.fit(cov_type='clustered', cluster_entity=True)
    
    print("   - 回归完成")
    print(f"   - 样本数: {len(X):,}")
    
    # 显示回归结果
    print("\n回归结果:")
    print("=" * 80)
    print(results)
    
    print("=" * 80)

    print(f"保存回归结果到: {output_file}")
    # with open(output_file, "w", newline="") as csvfile:
    # with open(f'{output_file}_{sheet_name}.csv', "w", newline="") as csvfile:
    # csvfile.write(results.summary.as_csv())
    # df = pd.DataFrame(pd.read_csv("output.csv"))
    with pd.ExcelWriter(output_file, engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        results_summary = pd.DataFrame({
            '变量': results.params.index,
            '系数': results.params.values,
            '标准误': results.std_errors.values,
            't值': results.tstats.values,
            'p值': results.pvalues.values,
            '置信区间下限': results.conf_int().iloc[:, 0].values,
            '置信区间上限': results.conf_int().iloc[:, 1].values
        })
        results_summary.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"   - 回归结果已保存到{sheet_name}工作表")
    return results
       
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='创建回归面板数据')
    parser.add_argument('--input_file', 
                       default='patent_analysis/regression_panel_data.xlsx',
                       help='输入文件路径')
    parser.add_argument('--output_file', 
                       default='patent_analysis/did_results.xlsx'
                    )
    args = parser.parse_args()
    # main(input_file=args.input_file, output_file=args.output_file)
    # main_lagged(province_dummy=True, stage_dummy=True, output_file= 'patent_analysis/did_results_lagged.xlsx')
    # stage_regress(args.input_file,'patent_analysis/stage.xlsx')
    region_regress('patent_analysis/regression_data_location.xlsx','patent_analysis/did_region.xlsx')
    # region_regress(input_file='patent_analysis/regression_panel_data.xlsx',output_file='patent_analysis/did_region.xlsx')
# 

