#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的preparedata.py功能
验证专利数量和被引证次数数据的处理
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_patent_data_processing():
    """测试专利数量数据处理"""
    print("=" * 60)
    print("测试专利数量数据处理")
    print("=" * 60)
    
    try:
        from preparedata import extract_regress_data_patents
        
        result = extract_regress_data_patents()
        
        if result:
            print("✅ 专利数量数据处理成功！")
            print(f"  - 输出文件: {result['excel_file']}")
            print(f"  - 处理公司数: {result['total_companies']}")
            print(f"  - 年份范围: {result['year_range']}")
            print(f"  - 数据类型: {result['data_type']}")
            return True
        else:
            print("❌ 专利数量数据处理失败")
            return False
            
    except Exception as e:
        print(f"❌ 专利数量数据处理出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_citation_data_processing():
    """测试被引证次数数据处理"""
    print("\n" + "=" * 60)
    print("测试被引证次数数据处理")
    print("=" * 60)
    
    try:
        from preparedata import extract_regress_data_citations
        
        result = extract_regress_data_citations()
        
        if result:
            print("✅ 被引证次数数据处理成功！")
            print(f"  - 输出文件: {result['excel_file']}")
            print(f"  - 处理公司数: {result['total_companies']}")
            print(f"  - 年份范围: {result['year_range']}")
            print(f"  - 数据类型: {result['data_type']}")
            return True
        else:
            print("❌ 被引证次数数据处理失败")
            return False
            
    except Exception as e:
        print(f"❌ 被引证次数数据处理出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_custom_data_processing():
    """测试自定义数据处理"""
    print("\n" + "=" * 60)
    print("测试自定义数据处理")
    print("=" * 60)
    
    try:
        from preparedata import extract_regress_data
        
        # 测试专利数量数据
        print("测试专利数量数据...")
        result_patents = extract_regress_data(
            patent_data_file='company_patent_yearly.xlsx', 
            data_type='patent_count'
        )
        
        if result_patents:
            print("✅ 自定义专利数量数据处理成功！")
            print(f"  - 输出文件: {result_patents['excel_file']}")
        else:
            print("❌ 自定义专利数量数据处理失败")
        
        # 测试被引证次数数据
        print("\n测试被引证次数数据...")
        result_citations = extract_regress_data(
            patent_data_file='company_patent_citations_yearly.xlsx', 
            data_type='citation_count'
        )
        
        if result_citations:
            print("✅ 自定义被引证次数数据处理成功！")
            print(f"  - 输出文件: {result_citations['excel_file']}")
            return True
        else:
            print("❌ 自定义被引证次数数据处理失败")
            return False
            
    except Exception as e:
        print(f"❌ 自定义数据处理出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试修改后的preparedata.py功能...")
    
    # 检查必要文件是否存在
    required_files = [
        'invest.xlsx',
        'company_patent_yearly.xlsx'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {missing_files}")
        print("请确保文件存在后再运行测试")
        return
    
    # 检查被引证次数数据文件
    citation_file = 'company_patent_citations_yearly.xlsx'
    if not os.path.exists(citation_file):
        print(f"⚠️  被引证次数数据文件不存在: {citation_file}")
        print("将跳过被引证次数数据处理测试")
        citation_file_exists = False
    else:
        citation_file_exists = True
    
    # 运行测试
    success_count = 0
    total_tests = 2 if citation_file_exists else 1
    
    # 测试1：专利数量数据处理
    if test_patent_data_processing():
        success_count += 1
    
    # 测试2：被引证次数数据处理（如果文件存在）
    if citation_file_exists:
        if test_citation_data_processing():
            success_count += 1
    
    # 测试3：自定义数据处理
    if test_custom_data_processing():
        success_count += 1
        total_tests += 1
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"成功测试: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查错误信息")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n测试程序执行出错：{e}")
        import traceback
        traceback.print_exc()

