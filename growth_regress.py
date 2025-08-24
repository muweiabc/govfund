import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
from linearmodels.panel import PanelOLS
import os
import traceback
import warnings
warnings.filterwarnings('ignore')

def check_required_files():
    """检查必要的文件是否存在"""
    required_files = ['gdp.xlsx', 'govfund_analysis_results.xlsx', '2003-2023各省分行业全社会固定资产投资额.xlsx','2000-2023年各省份城镇化水平.xlsx']
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
        df.columns = df.columns.astype(str)
        print(f"✓ 成功读取城镇化率数据")
        print(f"  数据形状: {df.shape}")
        print(f"  列名: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"✗ 读取城镇化率数据失败: {e}")
        return None

def read_fixed_invest():
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
   
        sheet_name = '总数据'
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
        
        return df[df['省级'] != '中国']
        
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

def read_employment_data():
    """读取就业人口数据文件"""
    try:
        print("\n正在读取就业人口数据文件...")
        df = pd.read_excel('就业人口.xlsx')
        print(f"✓ 成功读取就业人口数据文件")
        print(f"  数据形状: {df.shape}")
        print(f"  列名: {list(df.columns)}")
        
        # 检查必要的列
        required_columns = ['年度标识', '省份名称', '就业人员']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"✗ 错误: 就业人口文件缺少必要的列: {missing_columns}")
            print(f"  可用的列: {list(df.columns)}")
            return None
        
        # 过滤掉全国数据，只保留省份数据
        df = df[df['省份名称'] != '中国']
        
        # 检查数据类型
        print(f"  年度标识列数据类型: {df['年度标识'].dtype}")
        print(f"  省份名称列数据类型: {df['省份名称'].dtype}")
        print(f"  就业人员列数据类型: {df['就业人员'].dtype}")
        
        # 检查数据范围
        print(f"  年份范围: {df['年度标识'].min()} - {df['年度标识'].max()}")
        print(f"  省份数量: {df['省份名称'].nunique()}")
        print(f"  就业人员范围: {df['就业人员'].min():.2f} - {df['就业人员'].max():.2f}")
        
        return df
        
    except FileNotFoundError:
        print("✗ 错误: 找不到就业人口文件 '就业人口.xlsx'")
        return None
    except PermissionError:
        print("✗ 错误: 无法读取就业人口文件，可能是权限问题")
        return None
    except Exception as e:
        print(f"✗ 读取就业人口文件时发生未知错误: {e}")
        print(f"  错误类型: {type(e).__name__}")
        print("  详细错误信息:")
        traceback.print_exc()
        return None

def read_investment_detail_data():
    """读取省份年份投资详情数据文件"""
    try:
        print("\n正在读取省份年份投资详情数据...")
        df = pd.read_excel('govfund_analysis_results.xlsx', sheet_name='省份年份投资详情')
        print(f"✓ 成功读取投资详情数据")
        print(f"  数据形状: {df.shape}")
        print(f"  列名: {list(df.columns)}")
        
        # 检查必要的列
        required_columns = ['省份', '年份', '投资笔数']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"✗ 错误: 投资详情文件缺少必要的列: {missing_columns}")
            print(f"  可用的列: {list(df.columns)}")
            return None
        
        # 检查数据类型
        print(f"  年份列数据类型: {df['年份'].dtype}")
        print(f"  省份列数据类型: {df['省份'].dtype}")
        print(f"  投资笔数列数据类型: {df['投资笔数'].dtype}")
        
        # 检查数据范围
        print(f"  年份范围: {df['年份'].min()} - {df['年份'].max()}")
        print(f"  省份数量: {df['省份'].nunique()}")
        print(f"  投资笔数范围: {df['投资笔数'].min()} - {df['投资笔数'].max()}")
        
        return df
        
    except FileNotFoundError:
        print("✗ 错误: 找不到投资详情数据")
        return None
    except PermissionError:
        print("✗ 错误: 无法读取投资详情数据，可能是权限问题")
        return None
    except Exception as e:
        print(f"✗ 读取投资详情数据时发生未知错误: {e}")
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
        # print(f"  警告: 未找到 {province} 在 {year} 年的基金数据")
        return 0  # 返回0而不是None，避免后续错误
        
    except Exception as e:
        print(f"  错误: 在查找基金数据时发生异常: {e}")
        return 0

def regress():
    """执行回归分析"""
    try:
        print("=== GDP与投资笔数回归分析 ===")
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
        
        # 读取就业人口数据
        employment_df = read_employment_data()
        if employment_df is None:
            print("\n无法读取就业人口数据，程序终止")
            return
        
        # 读取投资详情数据
        investment_detail_df = read_investment_detail_data()
        if investment_detail_df is None:
            print("\n无法读取投资详情数据，程序终止")
            return
        
        # 读取固定资产投资数据
        investment_result = read_fixed_invest()
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
        panel_data = []
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
                    
                    # 获取投资笔数（替代基金数量）
                    investment_count = get_investment_count(province, year, investment_detail_df)
                    
                    pos = convert_province(province)
                    if str(year) not in urban_df.columns:
                        print('year not in urban_df.columns')
                    urban_rate = urban_df.loc[pos, str(year)]
                    
                    # 获取固定资产投资数据
                    investment_value = get_investment(province, year, investment_df, investment_col)
                    
                    # 获取就业人员数据
                    employment_value = get_employment(province, year, employment_df)
                    
                    matched_count += 1

                    # y.append(pgdp)
                    # x.append(investment_count)
                    panel_data.append({'province': province, 'year': year, '人均GDP': pgdp, '投资笔数': investment_count, '城镇化率': urban_rate, '固定资产投资': investment_value, '就业人员': employment_value})
                    # x.append([investment_count, urban_rate, np.log(investment_value)])
                        
            except Exception as e:
                print(f"  错误: 处理第{idx+1}行数据时发生异常: {e}")
                continue
        
        print(f"\n数据处理完成:")
        print(f"  总记录数: {total_count}")
        print(f"  匹配记录数: {matched_count}")
        print(f"  有效样本数: {len(y)}")
        
        panel_df = pd.DataFrame(panel_data)
        panel_df.set_index(['province', 'year'], inplace=True)
        # 创建数据框
        try:
            x_df = panel_df[['投资笔数','城镇化率','固定资产投资','就业人员']]
            y_df = panel_df['人均GDP']
            
            print(f"\n回归数据准备完成:")
            print(f"  自变量X形状: {x_df.shape}")
            print(f"  因变量y形状: {y_df.shape}")
            print(f"  投资笔数范围: {x_df['投资笔数'].min()} - {x_df['投资笔数'].max()}")
            print(f"  城镇化率范围: {x_df['城镇化率'].min():.4f} - {x_df['城镇化率'].max():.4f}")
            print(f"  固定资产投资范围: {x_df['固定资产投资'].min():.2f} - {x_df['固定资产投资'].max():.2f}")
            print(f"  就业人员范围: {x_df['就业人员'].min():.2f} - {x_df['就业人员'].max():.2f}")
            print(f"  人均GDP范围: {y_df.min():.2f} - {y_df.max():.2f}")
            
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
            if y_df.dtype == 'object':
                y_df = pd.to_numeric(y_df, errors='coerce')
            
        
            # 使用statsmodels.OLS进行回归
            # 添加常数项
            
            
            model = PanelOLS(y_df, x_df, entity_effects=False, time_effects=True)
    
            results = model.fit()
            
            print("\n=== 回归分析结果 ===")
            print(results)
            
            # 显示关键统计信息
            # print(f"\n关键统计信息:")
            # print(f"  R²: {results.rsquared:.4f}")
            # print(f"  调整R²: {results.rsquared_adj:.4f}")
            # print(f"  F统计量: {results.fvalue:.4f}")
            # print(f"  F统计量p值: {results.f_pvalue:.4f}")
            
            # # 显示系数
            # print(f"\n回归系数:")
            # for param, value in results.params.items():
            #     if param in results.pvalues.index:
            #         p_value = results.pvalues[param]
            #         t_value = results.tvalues[param]
            #         print(f"  {param}: {value:.4f} (t={t_value:.4f}, p={p_value:.4f})")
            
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
        
        # 在投资数据中查找匹配
        for idx, row in investment_df.iterrows():
            # 检查省份名称是否匹配（支持多种格式）
            if (province == row['地区'] and year == row['年份']):
                return row[investment_col]
        
        # 如果没有找到匹配的数据
        print(f"  警告: 未找到 {province} 在 {year} 年的投资数据")
        return 0  # 返回0而不是None，避免后续错误
        
    except Exception as e:
        print(f"  错误: 在查找投资数据时发生异常: {e}")
        return 0

def get_employment(province, year, employment_df):
    """根据省份和年份获取就业人员数据"""
    try:
        # 在就业人口数据中查找匹配
        for idx, row in employment_df.iterrows():
            # 检查省份名称和年份是否匹配
            if (province == row['省份名称'] and year == row['年度标识']):
                return row['就业人员']
        
        # 如果没有找到匹配的数据
        print(f"  警告: 未找到 {province} 在 {year} 年的就业人员数据")
        return 0  # 返回0而不是None，避免后续错误
        
    except Exception as e:
        print(f"  错误: 在查找就业人员数据时发生异常: {e}")
        return 0

def get_investment_count(province, year, investment_detail_df):
    """根据省份和年份获取投资笔数"""
    try:
        # 在投资详情数据中查找匹配
        for idx, row in investment_detail_df.iterrows():
            # 检查省份名称和年份是否匹配
            if (province == row['省份'] and year == row['年份']):
                return row['投资笔数']
        
        # 如果没有找到匹配的数据
        # print(f"  警告: 未找到 {province} 在 {year} 年的投资笔数数据")
        return 0  # 返回0而不是None，避免后续错误
        
    except Exception as e:
        print(f"  错误: 在查找投资笔数数据时发生异常: {e}")
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