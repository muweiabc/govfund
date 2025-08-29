#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专利被引证次数分析运行脚本
快速分析公司专利的被引证次数
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from company_patent_citation_analysis import (
    analyze_company_patent_citations,
    query_company_citations,
    get_top_cited_companies
)

def main():
    """主函数"""
    print("=" * 60)
    print("专利被引证次数分析工具")
    print("=" * 60)
    
    # 检查数据文件是否存在
    required_files = [
        'invest.xlsx',
        'data/trimpatent_all.csv'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("错误：以下必需文件不存在：")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("\n请确保文件存在后再运行分析。")
        return
    
    print("数据文件检查通过！")
    print()
    
    # 运行分析
    print("开始分析...")
    sparse_matrix, company_names, years = analyze_company_patent_citations()
    
    if sparse_matrix is not None:
        print("\n" + "=" * 60)
        print("分析完成！")
        print("=" * 60)
        
        # 显示基本统计信息
        print(f"成功分析了 {len(company_names)} 家公司的专利被引证情况")
        print(f"覆盖年份范围：{min(years)} - {max(years)}")
        print(f"数据矩阵大小：{sparse_matrix.shape}")
        
        # 显示前几家公司的被引证情况
        if company_names:
            print(f"\n前3家公司的被引证情况：")
            for i in range(min(3, len(company_names))):
                company = company_names[i]
                query_company_citations(company)
        
        # 显示被引证最多的公司
        print(f"\n被引证次数最多的前5家公司：")
        get_top_cited_companies(5)
        
        print(f"\n结果文件已保存：")
        print(f"  - company_patent_citations_yearly.xlsx (Excel格式)")
        print(f"  - company_patent_citations_matrix.pkl (Python对象)")
        
    else:
        print("分析失败，请检查数据文件格式和内容。")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断了程序执行。")
    except Exception as e:
        print(f"\n程序执行出错：{e}")
        import traceback
        traceback.print_exc()

