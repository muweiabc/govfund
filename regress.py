import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
import os
import traceback
import warnings
warnings.filterwarnings('ignore')

def check_required_files():
    """检查必要的文件是否存在"""
    required_files = ['gdp.xlsx', 'govfund_analysis_results.xlsx', '2003-2023各省分行业全社会固定资产投资额.xlsx']
    missing_files = []
    
    print("检查必要文件...")
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024
            print(f"✓ {file} 存在 ({size:.1f} KB)")
        else:
            print(f"✗ {file} 不存在")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n错误: 缺少必要文件: {missing_files}")
        print("请确保以下文件存在于当前目录:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    return True

def read_urban():
    """读取城镇化率数据"""
    try:
        df = pd.read_excel('2000-2023年各省份城镇化水平.xlsx',sheet_name='原始版本',index_col=0)
        print(f"✓ 成功读取城镇化率数据")
        print(f"  数据形状: {df.shape}")
        print(f"  列名: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"✗ 读取城镇化率数据失败: {e}")
        return None

def read_investment_data():
    """读取固定资产投资数据"""
    try:
        print("正在读取固定资产投资数据...")
        file_path = '2003-2023各省分行业全社会固定资产投资额.xlsx'
        
        if not os.path.exists(file_path):
            print(f"✗ 错误: 固定资产投资文件不存在 - {file_path}")
            return None
        
        # 尝试读取Excel文件
        xl_file = pd.ExcelFile(file_path)
        print(f"✓ 成功读取固定资产投资文件")
        print(f"  Sheet数量: {len(xl_file.sheet_names)}")
        print(f"  Sheet名称: {xl_file.sheet_names}")
        
        # 选择第一个sheet（假设包含主要数据）
        sheet_name = xl_file.sheet_names[0]
        print(f"  使用Sheet: {sheet_name}")
        
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"  数据形状: {df.shape}")
        print(f"  列名: {list(df.columns)}")
    
        investment_col = '合计/亿元'
        # 检查数据结构
        print(f"  投资列: {investment_col}")
        print(f"  前5行数据:")
        print(df.head())
        
        return df, investment_col
        
    except Exception as e:
        print(f"✗ 读取固定资产投资数据时发生错误: {e}")
        print(f"  错误类型: {type(e).__name__}")
        print("  详细错误信息:")
        traceback.print_exc()
        return None, None

def read_gdp_data():
    """读取GDP数据文件"""
    try:
        print("正在读取GDP数据文件...")
        df = pd.read_excel('gdp.xlsx')
        print(f"✓ 成功读取GDP文件")
        print(f"  数据形状: {df.shape}")
        print(f"  列名: {list(df.columns)}")
        
        # 检查必要的列
        required_columns = ['年份', '省级', '人均地区生产总值/元']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"✗ 错误: GDP文件缺少必要的列: {missing_columns}")
            print(f"  可用的列: {list(df.columns)}")
            print("  请检查GDP文件的列名是否正确")
            return None
        
        # 检查数据类型
        print(f"  年份列数据类型: {df['年份'].dtype}")
        print(f"  省级列数据类型: {df['省级'].dtype}")
        print(f"  人均GDP列数据类型: {df['人均地区生产总值/元'].dtype}")
        
        # 检查数据范围
        print(f"  年份范围: {df['年份'].min()} - {df['年份'].max()}")
        print(f"  省份数量: {df['省级'].nunique()}")
        print(f"  人均GDP范围: {df['人均地区生产总值/元'].min():.2f} - {df['人均地区生产总值/元'].max():.2f}")
        
        return df
        
    except FileNotFoundError:
        print("✗ 错误: 找不到GDP文件 'gdp.xlsx'")
        print("  请检查文件是否存在于当前目录")
        return None
    except PermissionError:
        print("✗ 错误: 无法读取GDP文件，可能是权限问题")
        print("  请确保文件没有被其他程序占用")
        return None
    except Exception as e:
        print(f"✗ 读取GDP文件时发生未知错误: {e}")
        print(f"  错误类型: {type(e).__name__}")
        print("  详细错误信息:")
        traceback.print_exc()
        return None

def read_fund_data():
    """读取基金分析结果文件"""
    try:
        print("\n正在读取基金分析结果文件...")
        df = pd.read_excel('govfund_analysis_results.xlsx',sheet_name='年份省份统计')
        print(f"✓ 成功读取基金分析结果文件")
        print(f"  数据形状: {df.shape}")
        print(f"  列名: {list(df.columns)}")
        
        # 检查必要的列
        required_columns = ['省份', '成立年份', '基金数量']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"✗ 错误: 基金文件缺少必要的列: {missing_columns}")
            print(f"  可用的列: {list(df.columns)}")
            print("  请先运行 analyze_govfund.py 生成正确的分析结果文件")
            return None
        
        # 检查数据类型
        print(f"  省份列数据类型: {df['省份'].dtype}")
        print(f"  成立年份列数据类型: {df['成立年份'].dtype}")
        print(f"  基金数量列数据类型: {df['基金数量'].dtype}")
        
        # 检查数据范围
        print(f"  年份范围: {df['成立年份'].min()} - {df['成立年份'].max()}")
        print(f"  省份数量: {df['省份'].nunique()}")
        print(f"  基金数量范围: {df['基金数量'].min()} - {df['基金数量'].max()}")
        
        return df
        
    except FileNotFoundError:
        print("✗ 错误: 找不到基金分析结果文件 'govfund_analysis_results.xlsx'")
        print("  请先运行 analyze_govfund.py 生成分析结果文件")
        return None
    except PermissionError:
        print("✗ 错误: 无法读取基金分析结果文件，可能是权限问题")
        print("  请确保文件没有被其他程序占用")
        return None
    except Exception as e:
        print(f"✗ 读取基金分析结果文件时发生未知错误: {e}")
        print(f"  错误类型: {type(e).__name__}")
        print("  详细错误信息:")
        traceback.print_exc()
        return None

def get_fund(province, year, df):
    """根据省份和年份获取基金数量"""
    try:
        for idx, row in df.iterrows():
            if row['省份'] == province and row['成立年份'] == year:
                return row['基金数量']
        
        # 如果没有找到匹配的数据
        print(f"  警告: 未找到 {province} 在 {year} 年的基金数据")
        return 0  # 返回0而不是None，避免后续错误
        
    except Exception as e:
        print(f"  错误: 在查找基金数据时发生异常: {e}")
        return 0

def regress():
    """执行回归分析"""
    try:
        print("=== GDP与基金数量回归分析 ===")
        print(f"当前工作目录: {os.getcwd()}")
        
        # 检查文件
        if not check_required_files():
            print("\n文件检查失败，程序终止")
            return
        
        # 读取数据
        gdp_df = read_gdp_data()
        if gdp_df is None:
            print("\n无法读取GDP数据，程序终止")
            return
        
        funds_df = read_fund_data()
        if funds_df is None:
            print("\n无法读取基金数据，程序终止")
            return
        
        urban_df = read_urban()
        if urban_df is None:
            print("\n无法读取城镇化率数据，程序终止")
            return
        
        # 读取固定资产投资数据
        investment_result = read_investment_data()
        if investment_result is None:
            print("\n无法读取固定资产投资数据，程序终止")
            return
        
        investment_df, investment_col = investment_result
        if investment_df is None:
            print("\n固定资产投资数据为空，程序终止")
            return
        
        # urban_df = urban_df.rename(columns={'年份': 'year', '省份': 'province', '城镇化率': 'urban_rate'})
        
        # 执行回归分析
        print("\n开始执行回归分析...")
        y = []
        x = []
        matched_count = 0
        total_count = 0
        
        for idx, row in gdp_df.iterrows():
            try:
                if row['年份'] > 2008 and row['年份'] < 2023:
                    total_count += 1
                    pgdp = row['人均地区生产总值/元']
                    province = row['省级']
                    year = row['年份']
                    
                    # 检查数据有效性
                    if pd.isna(pgdp) or pd.isna(province) or pd.isna(year):
                        print(f"  跳过第{idx+1}行: 包含空值")
                        continue
                    
                    fund = get_fund(province, year, funds_df)
                    pos = convert_province(province)
                    urban_rate = urban_df.loc[pos, str(year)]
                    
                    # 获取固定资产投资数据
                    investment_value = get_investment(province, year, investment_df, investment_col)
                    
                    if fund > 0:  # 只添加有基金数据的记录
                        matched_count += 1

                        y.append(pgdp)
                        # x.append(fund)
                        x.append([fund, urban_rate, investment_value])
                        
            except Exception as e:
                print(f"  错误: 处理第{idx+1}行数据时发生异常: {e}")
                continue
        
        print(f"\n数据处理完成:")
        print(f"  总记录数: {total_count}")
        print(f"  匹配记录数: {matched_count}")
        print(f"  有效样本数: {len(y)}")
        
        if len(y) == 0:
            print("✗ 错误: 没有有效的数据进行回归分析")
            print("可能的原因:")
            print("1. 年份范围不匹配")
            print("2. 省份名称不一致")
            print("3. 数据中没有重叠的年份-省份组合")
            return
        
        if len(y) < 10:
            print(f"⚠ 警告: 样本数量较少 ({len(y)})，可能影响回归结果的可靠性")
        
        # 创建数据框
        try:
            x_df = pd.DataFrame(x, columns=['基金数量','城镇化率','固定资产投资'])
            y_df = pd.DataFrame(y, columns=['人均GDP'])
            
            print(f"\n回归数据准备完成:")
            print(f"  自变量X形状: {x_df.shape}")
            print(f"  因变量y形状: {y_df.shape}")
            print(f"  基金数量范围: {x_df['基金数量'].min()} - {x_df['基金数量'].max()}")
            print(f"  城镇化率范围: {x_df['城镇化率'].min():.4f} - {x_df['城镇化率'].max():.4f}")
            print(f"  固定资产投资范围: {x_df['固定资产投资'].min():.2f} - {x_df['固定资产投资'].max():.2f}")
            print(f"  人均GDP范围: {y_df['人均GDP'].min():.2f} - {y_df['人均GDP'].max():.2f}")
            
        except Exception as e:
            print(f"✗ 错误: 创建数据框时发生异常: {e}")
            return
        
        # 执行回归
        try:
            print("\n正在执行OLS回归...")
            
            # 确保数据类型正确
            print("   - 检查数据类型...")
            for col in x_df.columns:
                print(f"     {col}: {x_df[col].dtype}")
                if x_df[col].dtype == 'object':
                    x_df[col] = pd.to_numeric(x_df[col], errors='coerce')
                elif x_df[col].dtype == 'bool':
                    x_df[col] = x_df[col].astype(int)
            
            print(f"     y_df: {y_df.dtypes}")
            if y_df['人均GDP'].dtype == 'object':
                y_df['人均GDP'] = pd.to_numeric(y_df['人均GDP'], errors='coerce')
            
            # 移除包含NaN的行
            print("   - 移除包含NaN的行...")
            initial_rows = len(x_df)
            valid_mask = ~(x_df.isna().any(axis=1) | y_df.isna().any(axis=1))
            x_df_clean = x_df[valid_mask]
            y_df_clean = y_df[valid_mask]
            final_rows = len(x_df_clean)
            print(f"     - 初始行数: {initial_rows}")
            print(f"     - 最终行数: {final_rows}")
            print(f"     - 移除行数: {initial_rows - final_rows}")
            
            if final_rows == 0:
                print("   ❌ 错误: 处理后没有有效数据")
                return
            
            if final_rows < len(x_df.columns) + 1:
                print(f"   ❌ 错误: 观测值数量({final_rows})少于变量数量({len(x_df.columns) + 1})")
                return
            
            # 使用statsmodels.OLS进行回归
            # 添加常数项
            x_df_with_constant = sm.add_constant(x_df_clean)
            
            model = OLS(y_df_clean, x_df_with_constant)
            results = model.fit()
            
            print("\n=== 回归分析结果 ===")
            print(results.summary())
            
            # 显示关键统计信息
            print(f"\n关键统计信息:")
            print(f"  R²: {results.rsquared:.4f}")
            print(f"  调整R²: {results.rsquared_adj:.4f}")
            print(f"  F统计量: {results.fvalue:.4f}")
            print(f"  F统计量p值: {results.f_pvalue:.4f}")
            
            # 显示系数
            print(f"\n回归系数:")
            for param, value in results.params.items():
                if param in results.pvalues.index:
                    p_value = results.pvalues[param]
                    t_value = results.tvalues[param]
                    print(f"  {param}: {value:.4f} (t={t_value:.4f}, p={p_value:.4f})")
            
        except Exception as e:
            print(f"✗ 错误: 执行回归分析时发生异常: {e}")
            print(f"  错误类型: {type(e).__name__}")
            print("  详细错误信息:")
            traceback.print_exc()
            return
        
        print("\n=== 回归分析完成 ===")
        
    except Exception as e:
        print(f"\n✗ 回归分析过程中发生未知错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        print("详细错误信息:")
        traceback.print_exc()

def convert_province(province):
    """转换省份名称格式"""
    if province.endswith('市') or province.endswith('省'):
        return province[:-1]
    else:
        return province

def get_investment(province, year, investment_df, investment_col):
    """根据省份和年份获取固定资产投资数据"""
    try:
        # 转换省份名称格式
        province_clean = convert_province(province)
        
        # 在投资数据中查找匹配
        for idx, row in investment_df.iterrows():
            # 检查省份名称是否匹配（支持多种格式）
            row_province = str(row.iloc[0]) if len(row) > 0 else ""
            if (province_clean in row_province or 
                province in row_province or 
                row_province in province or 
                row_province in province_clean):
                
                # 查找年份列
                for col in investment_df.columns:
                    if str(col) == str(year):
                        try:
                            investment_value = pd.to_numeric(row[col], errors='coerce')
                            if not pd.isna(investment_value):
                                return investment_value
                        except:
                            continue
        
        # 如果没有找到匹配的数据
        print(f"  警告: 未找到 {province} 在 {year} 年的投资数据")
        return 0  # 返回0而不是None，避免后续错误
        
    except Exception as e:
        print(f"  错误: 在查找投资数据时发生异常: {e}")
        return 0

if __name__ == "__main__":
    try:
        regress()
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"\n主程序执行过程中发生错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        print("详细错误信息:")
        traceback.print_exc()

    # df = read_urban()
    # print(df.loc['北京',2009])