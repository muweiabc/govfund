#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的流水线运行脚本
用于快速测试流水线功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_pipeline_test():
    """运行流水线测试"""
    print("=" * 60)
    print("专利分析流水线测试")
    print("=" * 60)
    
    try:
        from pipeline import PatentAnalysisPipeline
        
        # 创建流水线实例
        pipeline = PatentAnalysisPipeline()
        
        # 显示流水线状态
        pipeline.show_pipeline_status()
        
        # 询问是否运行完整流水线
        print("\n是否运行完整流水线？")
        print("注意：完整流水线可能需要较长时间")
        
        response = input("请输入 y/n: ").strip().lower()
        
        if response in ['y', 'yes', '是']:
            print("\n开始运行完整流水线...")
            success = pipeline.run_pipeline()
            
            if success:
                print("\n🎉 流水线执行成功！")
            else:
                print("\n⚠️ 流水线执行失败，请检查错误信息")
        else:
            print("跳过流水线执行")
            
    except ImportError as e:
        print(f"❌ 导入流水线模块失败: {e}")
        print("请确保pipeline.py文件存在且语法正确")
    except Exception as e:
        print(f"❌ 流水线测试出错: {e}")
        import traceback
        traceback.print_exc()

def run_single_step_test():
    """运行单个步骤测试"""
    print("=" * 60)
    print("单个步骤测试")
    print("=" * 60)
    
    try:
        from pipeline import PatentAnalysisPipeline
        
        # 创建流水线实例
        pipeline = PatentAnalysisPipeline()
        
        # 显示可用步骤
        print("可用步骤:")
        for i, step in enumerate(pipeline.pipeline_steps):
            print(f"  {i+1}. {step['name']}")
        
        # 选择要测试的步骤
        step_input = input("\n请输入要测试的步骤编号: ").strip()
        
        try:
            step_number = int(step_input) - 1
            if 0 <= step_number < len(pipeline.pipeline_steps):
                step = pipeline.pipeline_steps[step_number]
                step_name = step['name']
                
                print(f"\n测试步骤: {step_name}")
                print(f"描述: {step['description']}")
                
                # 检查输入文件
                missing_files = pipeline.check_files_exist(step['input_files'])
                if missing_files:
                    print(f"❌ 缺少输入文件: {missing_files}")
                    return
                
                # 执行步骤
                print(f"开始执行步骤: {step_name}")
                success, message = step['function']()
                
                if success:
                    print(f"✅ 步骤执行成功: {message}")
                else:
                    print(f"❌ 步骤执行失败: {message}")
                    
            else:
                print("❌ 无效的步骤编号")
                
        except ValueError:
            print("❌ 输入格式错误")
            
    except ImportError as e:
        print(f"❌ 导入流水线模块失败: {e}")
    except Exception as e:
        print(f"❌ 单步测试出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("专利分析流水线测试工具")
    print("=" * 50)
    
    print("请选择测试模式:")
    print("1. 流水线状态检查")
    print("2. 单个步骤测试")
    print("3. 完整流水线测试")
    
    try:
        choice = input("\n请输入选择 (1/2/3): ").strip()
        
        if choice == '1':
            # 流水线状态检查
            try:
                from pipeline import PatentAnalysisPipeline
                pipeline = PatentAnalysisPipeline()
                pipeline.show_pipeline_status()
            except Exception as e:
                print(f"❌ 状态检查失败: {e}")
                
        elif choice == '2':
            # 单个步骤测试
            run_single_step_test()
            
        elif choice == '3':
            # 完整流水线测试
            run_pipeline_test()
            
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n\n用户中断了程序执行")
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

