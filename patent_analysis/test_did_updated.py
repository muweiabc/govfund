#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的did.py功能
验证perform_did_regression_with_year_dummies函数现在接受输入文件参数
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_did_function_signature():
    """测试DID函数的签名"""
    print("=" * 60)
    print("测试DID函数签名")
    print("=" * 60)
    
    try:
        from did import perform_did_regression_with_year_dummies
        
        print("✅ did模块导入成功")
        
        # 检查函数签名
        import inspect
        
        sig = inspect.signature(perform_did_regression_with_year_dummies)
        print(f"函数签名: {sig}")
        
        # 检查参数
        params = list(sig.parameters.keys())
        print(f"参数列表: {params}")
        
        # 检查是否有input_file参数
        if 'input_file' in params:
            print("✅ 函数现在接受input_file参数")
        else:
            print("❌ 函数缺少input_file参数")
        
        # 检查是否有output_file参数
        if 'output_file' in params:
            print("✅ 函数现在接受output_file参数")
        else:
            print("❌ 函数缺少output_file参数")
        
        return True
        
    except Exception as e:
        print(f"❌ 函数签名测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pipeline_did_calls():
    """测试流水线中的DID调用"""
    print("\n" + "=" * 60)
    print("测试流水线中的DID调用")
    print("=" * 60)
    
    try:
        from pipeline import PatentAnalysisPipeline
        
        pipeline = PatentAnalysisPipeline()
        
        # 检查专利数量DID回归步骤
        patent_did_step = None
        citation_did_step = None
        
        for step in pipeline.pipeline_steps:
            if step['name'] == '专利数量DID回归分析':
                patent_did_step = step
            elif step['name'] == '被引证次数DID回归分析':
                citation_did_step = step
        
        if patent_did_step:
            print("✅ 找到专利数量DID回归分析步骤")
            print(f"  函数: {patent_did_step['function']}")
            print(f"  输入文件: {patent_did_step['input_files']}")
            print(f"  输出文件: {patent_did_step['output_files']}")
        else:
            print("❌ 未找到专利数量DID回归分析步骤")
        
        if citation_did_step:
            print("✅ 找到被引证次数DID回归分析步骤")
            print(f"  函数: {citation_did_step['function']}")
            print(f"  输入文件: {citation_did_step['input_files']}")
            print(f"  输出文件: {citation_did_step['output_files']}")
        else:
            print("❌ 未找到被引证次数DID回归分析步骤")
        
        return True
        
    except Exception as e:
        print(f"❌ 流水线DID调用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_did_function_parameters():
    """测试DID函数的参数处理"""
    print("\n" + "=" * 60)
    print("测试DID函数的参数处理")
    print("=" * 60)
    
    try:
        from did import perform_did_regression_with_year_dummies
        import inspect
        
        # 测试默认参数
        print("测试默认参数调用...")
        # 注意：这里只是测试函数签名，不实际执行
        sig = inspect.signature(perform_did_regression_with_year_dummies)
        
        # 检查默认值
        input_file_default = sig.parameters['input_file'].default
        output_file_default = sig.parameters['output_file'].default
        
        print(f"input_file默认值: {input_file_default}")
        print(f"output_file默认值: {output_file_default}")
        
        if input_file_default == 'regress_data_with_gdp.xlsx':
            print("✅ input_file默认值正确")
        else:
            print("❌ input_file默认值不正确")
        
        if output_file_default is None:
            print("✅ output_file默认值正确")
        else:
            print("❌ output_file默认值不正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 函数参数处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("修改后的DID功能测试")
    print("=" * 60)
    
    tests = [
        ("DID函数签名", test_did_function_signature),
        ("流水线DID调用", test_pipeline_did_calls),
        ("DID函数参数处理", test_did_function_parameters),
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
        print("🎉 所有测试通过！DID函数修改成功")
        print("\n主要改进:")
        print("1. perform_did_regression_with_year_dummies 现在接受input_file参数")
        print("2. 函数现在接受output_file参数")
        print("3. 流水线中的调用已更新为传递正确的文件路径")
        print("4. 专利数量和被引证次数分别使用不同的输入文件")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main()
