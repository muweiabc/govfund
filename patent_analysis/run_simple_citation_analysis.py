#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的专利被引证次数分析运行脚本
测试修改后的功能（无稀疏矩阵）
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    print("=" * 60)
    print("专利被引证次数分析工具（简化版）")
    print("=" * 60)
    
    try:
        # 导入分析模块
        from company_patent_citation_analysis import analyze_company_patent_citations
        
        print("开始分析...")
        result_df, company_names, years = analyze_company_patent_citations()
        
        if result_df is not None:
            print("\n" + "=" * 60)
            print("✅ 分析完成！")
            print("=" * 60)
            
            # 显示基本统计信息
            print(f"成功分析了 {len(company_names)} 家公司的专利被引证情况")
            print(f"覆盖年份范围：{min(years)} - {max(years)}")
            print(f"数据矩阵大小：{result_df.shape}")
            
            # 显示前几家公司的被引证情况
            if company_names:
                print(f"\n前3家公司的被引证情况：")
                for i in range(min(3, len(company_names))):
                    company = company_names[i]
                    citations_by_year = result_df.iloc[i]
                    total_citations = citations_by_year.sum()
                    print(f"{company}: 总计被引证 {total_citations} 次")
                    
                    # 显示有被引证的年份
                    years_with_citations = citations_by_year[citations_by_year > 0]
                    if len(years_with_citations) > 0:
                        print(f"  有被引证的年份: {dict(years_with_citations)}")
            
            print(f"\n结果文件已保存：")
            print(f"  - company_patent_citations_yearly.xlsx (Excel格式)")
            print(f"  - company_patent_citations_data.pkl (Python对象)")
            
        else:
            print("❌ 分析失败，请检查数据文件格式和内容。")
            
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保所有依赖包已安装")
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断了程序执行。")
    except Exception as e:
        print(f"\n程序执行出错：{e}")
        import traceback
        traceback.print_exc()

