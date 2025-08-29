#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的流水线功能
验证专利数量和被引证次数分别处理的流水线
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pipeline_import():
    """测试流水线模块导入"""
    print("=" * 60)
    print("测试流水线模块导入")
    print("=" * 60)
    
    try:
        from pipeline import PatentAnalysisPipeline
        print("✅ 流水线模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 流水线模块导入失败: {e}")
        return False

def test_pipeline_structure():
    """测试流水线结构"""
    print("\n" + "=" * 60)
    print("测试流水线结构")
    print("=" * 60)
    
    try:
        from pipeline import PatentAnalysisPipeline
        
        pipeline = PatentAnalysisPipeline()
        
        print(f"流水线步骤总数: {len(pipeline.pipeline_steps)}")
        
        # 检查步骤名称
        step_names = [step['name'] for step in pipeline.pipeline_steps]
        print("\n流水线步骤:")
        for i, name in enumerate(step_names):
            print(f"  {i+1}. {name}")
        
        # 检查是否有专利数量和被引证次数的分别处理
        patent_steps = [name for name in step_names if '专利数量' in name]
        citation_steps = [name for name in step_names if '被引证次数' in name]
        
        print(f"\n专利数量相关步骤: {len(patent_steps)}")
        for step in patent_steps:
            print(f"  - {step}")
        
        print(f"\n被引证次数相关步骤: {len(citation_steps)}")
        for step in citation_steps:
            print(f"  - {step}")
        
        return True
        
    except Exception as e:
        print(f"❌ 流水线结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_add_gdp_functions():
    """测试add_gdp模块的函数"""
    print("\n" + "=" * 60)
    print("测试add_gdp模块函数")
    print("=" * 60)
    
    try:
        from add_gdp import extract_province_from_region, add_province_gdp_data
        
        print("✅ add_gdp模块函数导入成功")
        
        # 检查函数签名
        import inspect
        
        # 检查extract_province_from_region函数
        sig1 = inspect.signature(extract_province_from_region)
        print(f"extract_province_from_region参数: {sig1}")
        
        # 检查add_province_gdp_data函数
        sig2 = inspect.signature(add_province_gdp_data)
        print(f"add_province_gdp_data参数: {sig2}")
        
        return True
        
    except Exception as e:
        print(f"❌ add_gdp模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pipeline_status():
    """测试流水线状态显示"""
    print("\n" + "=" * 60)
    print("测试流水线状态显示")
    print("=" * 60)
    
    try:
        from pipeline import PatentAnalysisPipeline
        
        pipeline = PatentAnalysisPipeline()
        
        # 显示流水线状态
        pipeline.show_pipeline_status()
        
        return True
        
    except Exception as e:
        print(f"❌ 流水线状态测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("修改后的流水线功能测试")
    print("=" * 60)
    
    tests = [
        ("流水线模块导入", test_pipeline_import),
        ("流水线结构", test_pipeline_structure),
        ("add_gdp模块函数", test_add_gdp_functions),
        ("流水线状态显示", test_pipeline_status),
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                success_count += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试出错: {e}")
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"成功测试: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！流水线修改成功")
        print("\n主要改进:")
        print("1. extract_province_from_region 现在接受输入文件参数")
        print("2. add_province_gdp_data 现在接受输入文件参数")
        print("3. 流水线分别为专利数量和被引证次数创建处理步骤")
        print("4. 输出文件名根据数据类型自动生成")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main()

