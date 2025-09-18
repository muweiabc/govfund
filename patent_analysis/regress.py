import pandas as pd
import numpy as np
import sys
import argparse
sys.path.append('.')
from linearmodels import PanelOLS

PATENT_COUNT = 'patent_count'
CITATION_COUNT = 'citation_count'
INVENTION_COUNT = 'invention_count'
INVENTION_CITATION = 'invention_citation'

def read_panel_data(input_file='patent_analysis/regression_panel_data.xlsx'):
    sheet_name = '面板数据'
    return pd.read_excel(input_file, sheet_name=sheet_name)

def main(province_dummy, stage_dummy, input_file='patent_analysis/regression_panel_data.xlsx', output_file='patent_analysis/did_results.xlsx'):
    panel_df = read_panel_data(input_file)
    panel_df.set_index(['company', 'year'], inplace=True)
   
    control_vars = ['treatment','treatment_post', 'GDP','城镇化率','固定资产投资','二产就业比例']

    if province_dummy:
        for col in panel_df.columns:
            if col.startswith('省份'):
                control_vars.append(col)
            # province_cols.append(col)
    # stage_cols = []
    if stage_dummy:
        for col in panel_df.columns:
            if col.startswith('投资阶段'):
                control_vars.append(col)

    X =panel_df[control_vars]
    y_patent = np.log(panel_df[PATENT_COUNT]+1)
    y_citation = np.log(panel_df[CITATION_COUNT]+1)
    y_invention = np.log(panel_df[INVENTION_COUNT]+1)
    y_invention_citation = np.log(panel_df[INVENTION_CITATION]+1)

    stas_x = panel_df.describe()
    stas_y_patent = y_patent.describe()
    stas_y_citation = y_citation.describe()
    stas_y_invention = y_invention.describe()
    stas_y_invention_citation = y_invention_citation.describe()

    ystats = pd.concat([stas_y_patent, stas_y_citation, stas_y_invention, stas_y_invention_citation], axis=1)
    ystats.columns = [PATENT_COUNT, CITATION_COUNT, INVENTION_COUNT, INVENTION_CITATION]
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        stas_x.to_excel(writer, sheet_name='回归变量统计')
        ystats.to_excel(writer, sheet_name='被解释变量统计')   

    regress(y_patent,X, output_file, PATENT_COUNT) 
    regress(y_citation,X, output_file, CITATION_COUNT) 
    regress(y_invention,X, output_file, INVENTION_COUNT) 
    regress(y_invention_citation,X, output_file, INVENTION_CITATION)             # stage_cols.append(col)
    
def main_lagged(province_dummy, stage_dummy, output_file):
    panel_df = read_panel_data()
    panel_df.set_index(['company', 'year'], inplace=True)
   
    control_vars = ['treatment','treatment_post', 'GDP','城镇化率','固定资产投资','二产就业比例']

    panel_df[f'lagged_{PATENT_COUNT}'] = panel_df[PATENT_COUNT].shift(1)
    panel_df[f'lagged_{CITATION_COUNT}'] = panel_df[CITATION_COUNT].shift(1)
    panel_df[f'lagged_{INVENTION_COUNT}'] = panel_df[INVENTION_COUNT].shift(1)
    panel_df[f'lagged_{INVENTION_CITATION}'] = panel_df[INVENTION_CITATION].shift(1)
    panel_df.dropna(inplace=True)

    if province_dummy:
        for col in panel_df.columns:
            if col.startswith('省份'):
                control_vars.append(col)
            # province_cols.append(col)
    # stage_cols = []
    if stage_dummy:
        for col in panel_df.columns:
            if col.startswith('投资阶段'):
                control_vars.append(col)

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
       
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='创建回归面板数据')
    parser.add_argument('--input_file', 
                       default='patent_analysis/regression_panel_data.xlsx',
                       help='输入文件路径')
    parser.add_argument('--output_file', 
                       default='patent_analysis/did_results.xlsx'
                    )
    args = parser.parse_args()
    main(province_dummy=True, stage_dummy=True, input_file=args.input_file, output_file=args.output_file)
    # main_lagged(province_dummy=True, stage_dummy=True, output_file= 'patent_analysis/did_results_lagged.xlsx')

