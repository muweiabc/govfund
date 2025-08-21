import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def read_gdp_data(file_path='gdp.xlsx'):
    """
    读取GDP数据文件
    
    Args:
        file_path (str): GDP文件路径
        
    Returns:
        pandas.DataFrame: GDP数据
    """
    try:
        df = pd.read_excel(file_path)
        print(f"成功读取GDP文件: {file_path}")
        print(f"GDP数据形状: {df.shape}")
        print(f"GDP列名: {list(df.columns)}")
        print("\nGDP数据前5行:")
        print(df.head())
        print("\nGDP数据类型:")
        print(df.dtypes)
        return df
    except Exception as e:
        print(f"读取GDP文件时出错: {e}")
        return None

def read_govfund_analysis_results(file_path='govfund_analysis_results.xlsx'):
    """
    读取政府基金分析结果
    
    Args:
        file_path (str): 分析结果文件路径
        
    Returns:
        pandas.DataFrame: 年份省份统计数据
    """
    try:
        # 读取年份省份统计sheet
        df = pd.read_excel(file_path, sheet_name='年份省份统计')
        print(f"成功读取基金分析结果: {file_path}")
        print(f"基金数据形状: {df.shape}")
        print(f"基金列名: {list(df.columns)}")
        print("\n基金数据前5行:")
        print(df.head())
        return df
    except Exception as e:
        print(f"读取基金分析结果时出错: {e}")
        return None

def process_gdp_data(gdp_df):
    """
    处理GDP数据，提取人均GDP信息
    
    Args:
        gdp_df (pandas.DataFrame): GDP原始数据
        
    Returns:
        pandas.DataFrame: 处理后的GDP数据
    """
    # 查找包含"人均地区生产总值"的列
    gdp_cols = [col for col in gdp_df.columns if '人均地区生产总值' in col]
    print(f"发现的人均GDP列: {gdp_cols}")
    
    if not gdp_cols:
        print("未找到人均GDP列，尝试查找其他相关列...")
        # 查找其他可能的GDP列
        gdp_cols = [col for col in gdp_df.columns if any(keyword in col for keyword in ['人均', 'GDP', '生产总值'])]
        print(f"找到的相关列: {gdp_cols}")
    
    if not gdp_cols:
        print("无法找到GDP相关列，请检查数据格式")
        return None
    
    # 使用第一个找到的GDP列
    gdp_col = gdp_cols[0]
    print(f"使用GDP列: {gdp_col}")
    
    # 查找年份列
    year_cols = [col for col in gdp_df.columns if any(keyword in col for keyword in ['年份', '年', 'year', 'Year'])]
    if not year_cols:
        # 如果没有年份列，尝试将第一列作为年份
        year_col = gdp_df.columns[0]
        print(f"使用第一列作为年份列: {year_col}")
    else:
        year_col = year_cols[0]
        print(f"使用年份列: {year_col}")
    
    # 查找省份列
    province_cols = [col for col in gdp_df.columns if any(keyword in col for keyword in ['省份', '地区', '省', '市', 'province', 'Province'])]
    if not province_cols:
        # 如果没有省份列，尝试将第二列作为省份
        province_col = gdp_df.columns[1]
        print(f"使用第二列作为省份列: {province_col}")
    else:
        province_col = province_cols[0]
        print(f"使用省份列: {province_col}")
    
    # 创建处理后的数据框
    processed_gdp = gdp_df[[year_col, province_col, gdp_col]].copy()
    processed_gdp.columns = ['年份', '省份', '人均GDP']
    
    # 清理数据
    processed_gdp = processed_gdp.dropna()
    
    # 确保年份是整数
    try:
        processed_gdp['年份'] = pd.to_numeric(processed_gdp['年份'], errors='coerce')
        processed_gdp = processed_gdp.dropna()
    except:
        print("年份转换失败")
    
    print(f"处理后的GDP数据形状: {processed_gdp.shape}")
    print("\n处理后的GDP数据前5行:")
    print(processed_gdp.head())
    
    return processed_gdp

def merge_gdp_fund_data(gdp_df, fund_df):
    """
    合并GDP和基金数据
    
    Args:
        gdp_df (pandas.DataFrame): 处理后的GDP数据
        fund_df (pandas.DataFrame): 基金数据
        
    Returns:
        pandas.DataFrame: 合并后的数据
    """
    # 确保列名一致
    if '成立年份' in fund_df.columns:
        fund_df = fund_df.rename(columns={'成立年份': '年份'})
    
    # 合并数据
    merged_df = pd.merge(fund_df, gdp_df, on=['年份', '省份'], how='inner')
    
    print(f"合并后数据形状: {merged_df.shape}")
    print("\n合并后数据前5行:")
    print(merged_df.head())
    
    # 检查数据质量
    print(f"\n数据质量检查:")
    print(f"唯一年份数: {merged_df['年份'].nunique()}")
    print(f"唯一省份数: {merged_df['省份'].nunique()}")
    print(f"总记录数: {len(merged_df)}")
    
    return merged_df

def perform_regression_analysis(merged_df):
    """
    执行回归分析
    
    Args:
        merged_df (pandas.DataFrame): 合并后的数据
        
    Returns:
        dict: 回归分析结果
    """
    results = {}
    
    # 准备数据
    X = merged_df['人均GDP'].values.reshape(-1, 1)
    y = merged_df['基金数量'].values
    
    # 1. 使用sklearn进行线性回归
    model = LinearRegression()
    model.fit(X, y)
    
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    
    sklearn_results = {
        'coefficient': model.coef_[0],
        'intercept': model.intercept_,
        'r2_score': r2,
        'mse': mse,
        'rmse': rmse
    }
    
    # 2. 使用statsmodels进行详细回归分析
    X_sm = sm.add_constant(X)
    model_sm = sm.OLS(y, X_sm).fit()
    
    statsmodels_results = {
        'summary': model_sm.summary(),
        'params': model_sm.params,
        'pvalues': model_sm.pvalues,
        'rsquared': model_sm.rsquared,
        'rsquared_adj': model_sm.rsquared_adj,
        'fvalue': model_sm.fvalue,
        'f_pvalue': model_sm.f_pvalue
    }
    
    results = {
        'sklearn': sklearn_results,
        'statsmodels': statsmodels_results,
        'data': merged_df
    }
    
    # 打印结果
    print("\n=== 回归分析结果 ===")
    print(f"样本数量: {len(merged_df)}")
    print(f"R² 决定系数: {r2:.4f}")
    print(f"均方误差 (MSE): {mse:.2f}")
    print(f"均方根误差 (RMSE): {rmse:.2f}")
    print(f"回归系数 (β): {model.coef_[0]:.6f}")
    print(f"截距项 (α): {model.intercept_:.2f}")
    
    print("\n=== 统计显著性检验 ===")
    print(f"F统计量: {statsmodels_results['fvalue']:.4f}")
    print(f"F检验p值: {statsmodels_results['f_pvalue']:.6f}")
    print(f"回归系数p值: {statsmodels_results['pvalues'][1]:.6f}")
    
    return results

def visualize_regression_results(regression_results):
    """
    可视化回归分析结果
    
    Args:
        regression_results (dict): 回归分析结果
    """
    if not regression_results:
        print("没有回归结果可以可视化")
        return
    
    data = regression_results['data']
    sklearn_results = regression_results['sklearn']
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('GDP与基金数量回归分析结果', fontsize=16)
    
    # 1. 散点图和回归线
    ax1 = axes[0, 0]
    ax1.scatter(data['人均GDP'], data['基金数量'], alpha=0.6, color='blue')
    
    # 绘制回归线
    X_line = np.linspace(data['人均GDP'].min(), data['人均GDP'].max(), 100).reshape(-1, 1)
    y_line = sklearn_results['coefficient'] * X_line + sklearn_results['intercept']
    ax1.plot(X_line, y_line, color='red', linewidth=2, label=f'回归线: y = {sklearn_results["coefficient"]:.6f}x + {sklearn_results["intercept"]:.2f}')
    
    ax1.set_xlabel('人均GDP (元)')
    ax1.set_ylabel('基金数量')
    ax1.set_title('基金数量 vs 人均GDP')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 残差图
    ax2 = axes[0, 1]
    y_pred = sklearn_results['coefficient'] * data['人均GDP'] + sklearn_results['intercept']
    residuals = data['基金数量'] - y_pred
    
    ax2.scatter(y_pred, residuals, alpha=0.6, color='green')
    ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)
    ax2.set_xlabel('预测值')
    ax2.set_ylabel('残差')
    ax2.set_title('残差图')
    ax2.grid(True, alpha=0.3)
    
    # 3. 按省份的基金数量分布
    ax3 = axes[1, 0]
    province_stats = data.groupby('省份')['基金数量'].sum().sort_values(ascending=False).head(10)
    ax3.barh(range(len(province_stats)), province_stats.values)
    ax3.set_yticks(range(len(province_stats)))
    ax3.set_yticklabels(province_stats.index)
    ax3.set_xlabel('基金总数')
    ax3.set_title('各省份基金数量分布 (前10名)')
    
    # 4. 按年份的趋势
    ax4 = axes[1, 1]
    yearly_stats = data.groupby('年份').agg({
        '基金数量': 'sum',
        '人均GDP': 'mean'
    }).reset_index()
    
    # 双y轴图
    ax4_twin = ax4.twinx()
    
    line1 = ax4.plot(yearly_stats['年份'], yearly_stats['基金数量'], 'b-o', label='基金数量', linewidth=2)
    line2 = ax4_twin.plot(yearly_stats['年份'], yearly_stats['人均GDP'], 'r-s', label='平均人均GDP', linewidth=2)
    
    ax4.set_xlabel('年份')
    ax4.set_ylabel('基金数量', color='blue')
    ax4_twin.set_ylabel('人均GDP (元)', color='red')
    ax4.set_title('基金数量和人均GDP年度趋势')
    
    # 合并图例
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax4.legend(lines, labels, loc='upper left')
    
    plt.tight_layout()
    plt.show()

def save_regression_results(regression_results, output_file='gdp_fund_regression_results.xlsx'):
    """
    保存回归分析结果
    
    Args:
        regression_results (dict): 回归分析结果
        output_file (str): 输出文件名
    """
    if not regression_results:
        print("没有结果可以保存")
        return
    
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 保存合并后的数据
            regression_results['data'].to_excel(writer, sheet_name='合并数据', index=False)
            
            # 保存回归统计结果
            sklearn_results = regression_results['sklearn']
            stats_df = pd.DataFrame({
                '指标': ['R²决定系数', '均方误差(MSE)', '均方根误差(RMSE)', '回归系数(β)', '截距项(α)'],
                '数值': [sklearn_results['r2_score'], sklearn_results['mse'], sklearn_results['rmse'], 
                        sklearn_results['coefficient'], sklearn_results['intercept']]
            })
            stats_df.to_excel(writer, sheet_name='回归统计', index=False)
            
            # 保存省份统计
            province_stats = regression_results['data'].groupby('省份').agg({
                '基金数量': 'sum',
                '人均GDP': 'mean'
            }).reset_index()
            province_stats.to_excel(writer, sheet_name='省份统计', index=False)
            
            # 保存年份统计
            yearly_stats = regression_results['data'].groupby('年份').agg({
                '基金数量': 'sum',
                '人均GDP': 'mean'
            }).reset_index()
            yearly_stats.to_excel(writer, sheet_name='年份统计', index=False)
        
        print(f"回归分析结果已保存到: {output_file}")
    except Exception as e:
        print(f"保存文件时出错: {e}")

def main():
    """
    主函数
    """
    print("=== GDP与基金数量回归分析 ===")
    
    # 1. 读取GDP数据
    print("\n1. 读取GDP数据...")
    gdp_df = read_gdp_data()
    if gdp_df is None:
        return
    
    # 2. 处理GDP数据
    print("\n2. 处理GDP数据...")
    processed_gdp = process_gdp_data(gdp_df)
    if processed_gdp is None:
        return
    
    # 3. 读取基金分析结果
    print("\n3. 读取基金分析结果...")
    fund_df = read_govfund_analysis_results()
    if fund_df is None:
        return
    
    # 4. 合并数据
    print("\n4. 合并GDP和基金数据...")
    merged_df = merge_gdp_fund_data(processed_gdp, fund_df)
    if merged_df is None or len(merged_df) == 0:
        print("合并后没有数据，无法进行回归分析")
        return
    
    # 5. 执行回归分析
    print("\n5. 执行回归分析...")
    regression_results = perform_regression_analysis(merged_df)
    
    # 6. 可视化结果
    print("\n6. 生成可视化图表...")
    visualize_regression_results(regression_results)
    
    # 7. 保存结果
    print("\n7. 保存分析结果...")
    save_regression_results(regression_results)
    
    print("\n=== 分析完成 ===")

if __name__ == "__main__":
    main()
