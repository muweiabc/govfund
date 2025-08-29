#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试专利被引证次数分析功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有必要的包是否能正常导入"""
    print("测试包导入...")
    
    try:
        import pandas as pd
        print("✓ pandas 导入成功")
    except ImportError as e:
        print(f"✗ pandas 导入失败: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ numpy 导入成功")
    except ImportError as e:
        print(f"✗ numpy 导入失败: {e}")
        return False
    
    try:
        from scipy.sparse import csr_matrix
        print("✓ scipy 导入成功")
    except ImportError as e:
        print(f"✗ scipy 导入失败: {e}")
        return False
    
    try:
        import tqdm
        print("✓ tqdm 导入成功")
    except ImportError as e:
        print(f"✗ tqdm 导入失败: {e}")
        return False
    
    try:
        import openpyxl
        print("✓ openpyxl 导入成功")
    except ImportError as e:
        print(f"✗ openpyxl 导入失败: {e}")
        return False
    
    return True

def test_file_access():
    """测试文件访问权限"""
    print("\n测试文件访问...")
    
    # 测试invest.xlsx
    if os.path.exists('invest.xlsx'):
        print("✓ invest.xlsx 文件存在")
        try:
            import pandas as pd
            df = pd.read_excel('invest.xlsx')
            if '融资主体' in df.columns:
                print(f"✓ invest.xlsx 包含'融资主体'列，共 {len(df['融资主体'].dropna().unique())} 家唯一公司")
            else:
                print("✗ invest.xlsx 不包含'融资主体'列")
                return False
        except Exception as e:
            print(f"✗ 读取invest.xlsx失败: {e}")
            return False
    else:
        print("✗ invest.xlsx 文件不存在")
        return False
    
    # 测试专利数据文件
    patent_file = 'data/trimpatent_all.csv'
    if os.path.exists(patent_file):
        print(f"✓ {patent_file} 文件存在")
        file_size = os.path.getsize(patent_file)
        print(f"  文件大小: {file_size / (1024**3):.2f} GB")
        
        # 尝试读取前几行
        try:
            import pandas as pd
            # 只读取前几行来检查列名
            sample_df = pd.read_csv(patent_file, nrows=5)
            print(f"  列名: {sample_df.columns.tolist()}")
            
            required_cols = ['申请人', '申请年份']
            missing_cols = [col for col in required_cols if col not in sample_df.columns]
            
            if not missing_cols:
                print("✓ 包含必要的列")
            else:
                print(f"✗ 缺少必要的列: {missing_cols}")
                return False
                
        except Exception as e:
            print(f"✗ 读取专利数据文件失败: {e}")
            return False
    else:
        print(f"✗ {patent_file} 文件不存在")
        return False
    
    return True

def test_analysis_module():
    """测试分析模块"""
    print("\n测试分析模块...")
    
    try:
        from company_patent_citation_analysis import (
            analyze_company_patent_citations,
            query_company_citations,
            get_top_cited_companies
        )
        print("✓ 分析模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ 分析模块导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("专利被引证次数分析工具 - 功能测试")
    print("=" * 60)
    
    # 测试1：包导入
    if not test_imports():
        print("\n❌ 包导入测试失败，请安装缺失的依赖包")
        return
    
    # 测试2：文件访问
    if not test_file_access():
        print("\n❌ 文件访问测试失败，请检查文件路径和权限")
        return
    
    # 测试3：分析模块
    if not test_analysis_module():
        print("\n❌ 分析模块测试失败，请检查代码文件")
        return
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    print("\n现在可以运行分析：")
    print("python run_citation_analysis.py")
    
    # 询问是否立即运行分析
    try:
        response = input("\n是否立即运行分析？(y/n): ").strip().lower()
        if response in ['y', 'yes', '是']:
            print("\n开始运行分析...")
            from company_patent_citation_analysis import analyze_company_patent_citations
            result = analyze_company_patent_citations()
            if result[0] is not None:
                print("✅ 分析完成！")
            else:
                print("❌ 分析失败")
    except KeyboardInterrupt:
        print("\n\n用户中断了程序执行。")
    except Exception as e:
        print(f"\n运行分析时出错: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n测试程序执行出错：{e}")
        import traceback
        traceback.print_exc()

