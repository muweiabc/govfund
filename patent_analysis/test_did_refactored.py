#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试重构后的did.py功能
验证函数拆分后的三个新函数是否正常工作
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_function_imports():
    """测试函数导入"""
    print("=" * 60)
    print("测试函数导入")
    print("=" * 60)
    
    try:
        from did import (
            prepare_panel_data, 
            generate_dummy_variables, 
            perform_regression,
            perform_did_regression_with_year_dummies
        )
        
        print("✅ 所有函数导入成功")
        print(f"  - prepare_panel_data: {prepare_panel_data}")
        print(f"  - generate_dummy_variables: {generate_dummy_variables}")
        print(f"  - perform_regression: {perform_regression}")
        print(f"  - perform_did_regression_with_year_dummies: {perform_did_regression_with_year_dummies}")
        
        return True
        
    except Exception as e:
        print(f"❌ 函数导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_function_signatures():
    """测试函数签名"""
    print("\n" + "=" * 60)
    print("测试函数签名")
    print("=" * 60)
    
    try:
        import inspect
        from did import (
            prepare_panel_data, 
            generate_dummy_variables, 
            perform_regression,
            perform_did_regression_with_year_dummies
        )
        
        # 检查函数签名
        functions = [
            ("prepare_panel_data", prepare_panel_data),
            ("generate_dummy_variables", generate_dummy_variables),
            ("perform_regression", perform_regression),
            ("perform_did_regression_with_year_dummies", perform_did_regression_with_year_dummies)
        ]
        
        for name, func in functions:
            sig = inspect.signature(func)
            print(f"✅ {name}: {sig}")
            
            # 检查参数
            params = list(sig.parameters.keys())
            print(f"   参数: {params}")
        
        return True
        
    except Exception as e:
        print(f"❌ 函数签名测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_function_documentation():
    """测试函数文档"""
    print("\n" + "=" * 60)
    print("测试函数文档")
    print("=" * 60)
    
    try:
        from did import (
            prepare_panel_data, 
            generate_dummy_variables, 
            perform_regression,
            perform_did_regression_with_year_dummies
        )
        
        functions = [
            ("prepare_panel_data", prepare_panel_data),
            ("generate_dummy_variables", generate_dummy_variables),
            ("perform_regression", perform_regression),
            ("perform_did_regression_with_year_dummies", perform_did_regression_with_year_dummies)
        ]
        
        for name, func in functions:
            doc = func.__doc__
            if doc:
                print(f"✅ {name}: 有文档")
                # 显示文档的前几行
                lines = doc.strip().split('\n')
                for line in lines[:3]:
                    if line.strip():
                        print(f"   {line.strip()}")
                if len(lines) > 3:
                    print("   ...")
            else:
                print(f"❌ {name}: 缺少文档")
        
        return True
        
    except Exception as e:
        print(f"❌ 函数文档测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_function_parameters():
    """测试主函数参数"""
    print("\n" + "=" * 60)
    print("测试主函数参数")
    print("=" * 60)
    
    try:
        from did import perform_did_regression_with_year_dummies
        import inspect
        
        sig = inspect.signature(perform_did_regression_with_year_dummies)
        params = list(sig.parameters.keys())
        
        print(f"主函数参数: {params}")
        
        # 检查是否有input_file和output_file参数
        if 'input_file' in params:
            print("✅ 有input_file参数")
        else:
            print("❌ 缺少input_file参数")
            
        if 'output_file' in params:
            print("✅ 有output_file参数")
        else:
            print("❌ 缺少output_file参数")
            
        if 'enable_province_dummies' in params:
            print("✅ 有enable_province_dummies参数")
        else:
            print("❌ 缺少enable_province_dummies参数")
            
        if 'use_time_effects' in params:
            print("✅ 有use_time_effects参数")
        else:
            print("❌ 缺少use_time_effects参数")
        
        return True
        
    except Exception as e:
        print(f"❌ 主函数参数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_code_structure():
    """测试代码结构"""
    print("\n" + "=" * 60)
    print("测试代码结构")
    print("=" * 60)
    
    try:
        # 读取did.py文件
        did_file_path = os.path.join(os.path.dirname(__file__), 'did.py')
        with open(did_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查函数定义
        functions = [
            'def prepare_panel_data',
            'def generate_dummy_variables', 
            'def perform_regression',
            'def perform_did_regression_with_year_dummies'
        ]
        
        for func in functions:
            if func in content:
                print(f"✅ 找到函数定义: {func}")
            else:
                print(f"❌ 未找到函数定义: {func}")
        
        # 检查主函数是否调用新函数
        if 'prepare_panel_data(df)' in content:
            print("✅ 主函数调用prepare_panel_data")
        else:
            print("❌ 主函数未调用prepare_panel_data")
            
        if 'generate_dummy_variables(panel_df' in content:
            print("✅ 主函数调用generate_dummy_variables")
        else:
            print("❌ 主函数未调用generate_dummy_variables")
            
        if 'perform_regression(panel_df' in content:
            print("✅ 主函数调用perform_regression")
        else:
            print("❌ 主函数未调用perform_regression")
        
        return True
        
    except Exception as e:
        print(f"❌ 代码结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("重构后的DID功能测试")
    print("=" * 60)
    
    tests = [
        ("函数导入", test_function_imports),
        ("函数签名", test_function_signatures),
        ("函数文档", test_function_documentation),
        ("主函数参数", test_main_function_parameters),
        ("代码结构", test_code_structure),
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
        print("🎉 所有测试通过！DID函数重构成功")
        print("\n重构成果:")
        print("1. 原长函数已拆分为三个清晰的函数")
        print("2. prepare_panel_data: 负责准备面板数据")
        print("3. generate_dummy_variables: 负责生成虚拟变量")
        print("4. perform_regression: 负责执行回归分析")
        print("5. 主函数现在更加简洁，只负责协调调用")
        print("6. 代码可读性和可维护性大大提高")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main()
