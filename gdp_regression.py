import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import warnings
import os
import traceback
warnings.filterwarnings('ignore')

def read_gdp_data(file_path='gdp.xlsx'):
    """读取GDP数据"""
    try:
        print(f"正在尝试读取GDP文件: {file_path}")
        print(f"当前工作目录: {os.getcwd()}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: GDP文件不存在 - {file_path}")
            return None
            
        df = pd.read_excel(file_path)
        print(f"成功读取GDP文件: {file_path}")
        print(f"GDP数据形状: {df.shape}")
        print(f"GDP列名: {list(df.columns)}")
        
        # 检查必要的列
        required_columns = ['人均地区生产总值']
        missing_columns = [col for col in required_columns if not any(keyword in col for keyword in ['人均', 'GDP', '生产总值'])]
        if missing_columns:
            print(f"警告: 可能缺少GDP相关列")
            print(f"建议查找包含'人均'、'GDP'、'生产总值'等关键词的列")
        
        return df
    except FileNotFoundError as e:
        print(f"GDP文件未找到错误: {e}")
        print(f"请检查文件路径: {file_path}")
        return None
    except PermissionError as e:
        print(f"GDP文件权限错误: {e}")
        print("请确保文件没有被其他程序占用")
        return None
    except Exception as e:
        print(f"读取GDP文件时发生未知错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        print("详细错误信息:")
        traceback.print_exc()
        return None

def read_fund_results(file_path='govfund_analysis_results.xlsx'):
    """读取基金分析结果"""
    try:
        print(f"正在尝试读取基金分析结果: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: 基金分析结果文件不存在 - {file_path}")
            print("请先运行 analyze_govfund.py 生成分析结果文件")
            return None
            
        # 检查sheet是否存在
        try:
            df = pd.read_excel(file_path, sheet_name='年份省份统计')
            print(f"成功读取基金分析结果: {file_path}")
            print(f"基金数据形状: {df.shape}")
            print(f"基金列名: {list(df.columns)}")
            
            # 检查必要的列
            required_columns = ['成立年份', '省份', '基金数量']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"警告: 缺少必要的列: {missing_columns}")
                print(f"可用的列: {list(df.columns)}")
            
            return df
        except ValueError as e:
            print(f"错误: 找不到'年份省份统计'sheet - {e}")
            print("可用的sheet名称:")
            try:
                xl_file = pd.ExcelFile(file_path)
                print(xl_file.sheet_names)
            except:
                print("无法读取sheet名称")
            return None
            
    except FileNotFoundError as e:
        print(f"基金分析结果文件未找到错误: {e}")
        print(f"请检查文件路径: {file_path}")
        return None
    except PermissionError as e:
        print(f"基金分析结果文件权限错误: {e}")
        print("请确保文件没有被其他程序占用")
        return None
    except Exception as e:
        print(f"读取基金分析结果时发生未知错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        print("详细错误信息:")
        traceback.print_exc()
        return None

def process_gdp_data(gdp_df):
    """处理GDP数据，提取人均GDP信息"""
    try:
        print("开始处理GDP数据...")
        
        # 查找包含"人均地区生产总值"的列
        gdp_cols = [col for col in gdp_df.columns if '人均地区生产总值' in col]
        if not gdp_cols:
            gdp_cols = [col for col in gdp_df.columns if any(keyword in col for keyword in ['人均', 'GDP'])]
        
        if not gdp_cols:
            print("错误: 无法找到GDP相关列")
            print(f"可用的列: {list(gdp_df.columns)}")
            print("建议查找包含'人均'、'GDP'、'生产总值'等关键词的列")
            return None
        
        gdp_col = gdp_cols[0]
        print(f"使用GDP列: {gdp_col}")
        print(f"GDP列前5个值: {gdp_df[gdp_col].head().tolist()}")
        
        # 查找年份和省份列
        year_col = gdp_df.columns[0]  # 假设第一列是年份
        province_col = gdp_df.columns[1]  # 假设第二列是省份
        
        print(f"使用年份列: {year_col}")
        print(f"使用省份列: {province_col}")
        print(f"年份列前5个值: {gdp_df[year_col].head().tolist()}")
        print(f"省份列前5个值: {gdp_df[province_col].head().tolist()}")
        
        # 检查数据类型
        print(f"年份列数据类型: {gdp_df[year_col].dtype}")
        print(f"省份列数据类型: {gdp_df[province_col].dtype}")
        print(f"GDP列数据类型: {gdp_df[gdp_col].dtype}")
        
        # 创建处理后的数据框
        processed_gdp = gdp_df[[year_col, province_col, gdp_col]].copy()
        processed_gdp.columns = ['年份', '省份', '人均GDP']
        
        # 清理数据
        print(f"处理前数据形状: {processed_gdp.shape}")
        processed_gdp = processed_gdp.dropna()
        print(f"处理后数据形状: {processed_gdp.shape}")
        
        # 检查数据质量
        print(f"唯一年份数: {processed_gdp['年份'].nunique()}")
        print(f"唯一省份数: {processed_gdp['省份'].nunique()}")
        
        return processed_gdp
        
    except Exception as e:
        print(f"处理GDP数据时发生错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        print("详细错误信息:")
        traceback.print_exc()
        return None

def merge_and_regress(gdp_df, fund_df):
    """合并数据并执行回归分析"""
    try:
        print("开始合并数据...")
        
        # 检查输入数据
        print(f"GDP数据形状: {gdp_df.shape}")
        print(f"基金数据形状: {fund_df.shape}")
        print(f"GDP数据列: {list(gdp_df.columns)}")
        print(f"基金数据列: {list(fund_df.columns)}")
        
        # 确保列名一致
        if '成立年份' in fund_df.columns:
            fund_df = fund_df.rename(columns={'成立年份': '年份'})
            print("已将'成立年份'重命名为'年份'")
        
        # 检查合并键
        print(f"GDP数据中的年份范围: {gdp_df['年份'].min()} - {gdp_df['年份'].max()}")
        print(f"基金数据中的年份范围: {fund_df['年份'].min()} - {fund_df['年份'].max()}")
        print(f"GDP数据中的省份: {sorted(gdp_df['省份'].unique())}")
        print(f"基金数据中的省份: {sorted(fund_df['省份'].unique())}")
        
        # 合并数据
        print("正在合并数据...")
        merged_df = pd.merge(gdp_df, fund_df, on=['年份', '省份'], how='inner')
        print(f"合并后数据形状: {merged_df.shape}")
        
        if len(merged_df) == 0:
            print("错误: 合并后没有数据")
            print("可能的原因:")
            print("1. 年份格式不匹配")
            print("2. 省份名称不匹配")
            print("3. 数据中没有重叠的年份-省份组合")
            return None
        
        # 检查合并后的数据
        print(f"合并后数据列: {list(merged_df.columns)}")
        print(f"合并后年份范围: {merged_df['年份'].min()} - {merged_df['年份'].max()}")
        print(f"合并后省份数量: {merged_df['省份'].nunique()}")
        
        # 执行回归分析
        print("开始执行回归分析...")
        X = merged_df['人均GDP'].values.reshape(-1, 1)
        y = merged_df['基金数量'].values
        
        print(f"自变量X形状: {X.shape}")
        print(f"因变量y形状: {y.shape}")
        print(f"人均GDP范围: {X.min():.2f} - {X.max():.2f}")
        print(f"基金数量范围: {y.min()} - {y.max()}")
        
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        
        print(f"\n=== 回归分析结果 ===")
        print(f"样本数量: {len(merged_df)}")
        print(f"R² 决定系数: {r2:.4f}")
        print(f"回归系数 (β): {model.coef_[0]:.6f}")
        print(f"截距项 (α): {model.intercept_:.2f}")
        print(f"均方误差 (MSE): {mse:.2f}")
        
        # 可视化
        print("正在生成可视化图表...")
        plt.figure(figsize=(12, 8))
        
        # 散点图和回归线
        plt.subplot(2, 2, 1)
        plt.scatter(merged_df['人均GDP'], merged_df['基金数量'], alpha=0.6)
        X_line = np.linspace(merged_df['人均GDP'].min(), merged_df['人均GDP'].max(), 100)
        y_line = model.coef_[0] * X_line + model.intercept_
        plt.plot(X_line, y_line, 'r-', linewidth=2)
        plt.xlabel('人均GDP (元)')
        plt.ylabel('基金数量')
        plt.title('基金数量 vs 人均GDP')
        plt.grid(True, alpha=0.3)
        
        # 残差图
        plt.subplot(2, 2, 2)
        residuals = y - y_pred
        plt.scatter(y_pred, residuals, alpha=0.6, color='green')
        plt.axhline(y=0, color='red', linestyle='--')
        plt.xlabel('预测值')
        plt.ylabel('残差')
        plt.title('残差图')
        plt.grid(True, alpha=0.3)
        
        # 按省份分布
        plt.subplot(2, 2, 3)
        province_stats = merged_df.groupby('省份')['基金数量'].sum().sort_values(ascending=False).head(10)
        plt.barh(range(len(province_stats)), province_stats.values)
        plt.yticks(range(len(province_stats)), province_stats.index)
        plt.xlabel('基金总数')
        plt.title('各省份基金数量分布 (前10名)')
        
        # 按年份趋势
        plt.subplot(2, 2, 4)
        yearly_stats = merged_df.groupby('年份').agg({
            '基金数量': 'sum',
            '人均GDP': 'mean'
        }).reset_index()
        
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        
        line1 = ax1.plot(yearly_stats['年份'], yearly_stats['基金数量'], 'b-o', label='基金数量')
        line2 = ax2.plot(yearly_stats['年份'], yearly_stats['人均GDP'], 'r-s', label='平均人均GDP')
        
        ax1.set_xlabel('年份')
        ax1.set_ylabel('基金数量', color='blue')
        ax2.set_ylabel('人均GDP (元)', color='red')
        ax1.set_title('基金数量和人均GDP年度趋势')
        
        plt.tight_layout()
        plt.show()
        
        return merged_df, model
        
    except Exception as e:
        print(f"合并数据或回归分析时发生错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        print("详细错误信息:")
        traceback.print_exc()
        return None

def main():
    """主函数"""
    try:
        print("=== GDP与基金数量回归分析 ===")
        print(f"当前工作目录: {os.getcwd()}")
        
        # 读取数据
        print("\n步骤1: 读取GDP数据...")
        gdp_df = read_gdp_data()
        if gdp_df is None:
            print("无法读取GDP数据，程序终止")
            return
        
        print("\n步骤2: 读取基金分析结果...")
        fund_df = read_fund_results()
        if fund_df is None:
            print("无法读取基金分析结果，程序终止")
            print("请先运行 analyze_govfund.py 生成分析结果文件")
            return
        
        # 处理数据
        print("\n步骤3: 处理GDP数据...")
        processed_gdp = process_gdp_data(gdp_df)
        if processed_gdp is None:
            print("无法处理GDP数据，程序终止")
            return
        
        # 执行回归分析
        print("\n步骤4: 执行回归分析...")
        results = merge_and_regress(processed_gdp, fund_df)
        
        if results:
            print("\n=== 分析完成 ===")
            print("回归分析成功完成！")
        else:
            print("\n=== 分析失败 ===")
            print("回归分析过程中出现错误")
            
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"\n主程序执行过程中发生未知错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        print("详细错误信息:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
