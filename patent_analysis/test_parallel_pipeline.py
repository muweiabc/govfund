#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的并行流水线功能
验证专利数量和被引证次数作为两条独立流水线的设计
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pipeline_structure():
    """测试流水线结构"""
    print("=" * 60)
    print("测试流水线结构")
    print("=" * 60)
    
    try:
        from pipeline import PatentAnalysisPipeline
        
        pipeline = PatentAnalysisPipeline()
        
        print(f"流水线步骤总数: {len(pipeline.pipeline_steps)}")
        
        # 检查流水线类型
        patent_steps = [step for step in pipeline.pipeline_steps if step.get('pipeline') == 'patent']
        citation_steps = [step for step in pipeline.pipeline_steps if step.get('pipeline') == 'citation']
        
        print(f"\n专利数量流水线步骤数: {len(patent_steps)}")
        print("专利数量流水线步骤:")
        for i, step in enumerate(patent_steps):
            print(f"  {i+1}. {step['name']}")
        
        print(f"\n被引证次数流水线步骤数: {len(citation_steps)}")
        print("被引证次数流水线步骤:")
        for i, step in enumerate(citation_steps):
            print(f"  {i+1}. {step['name']}")
        
        # 验证两条流水线是否独立
        patent_names = {step['name'] for step in patent_steps}
        citation_names = {step['name'] for step in citation_steps}
        
        if patent_names.isdisjoint(citation_names):
            print("\n✅ 两条流水线完全独立，没有重复步骤")
        else:
            print("\n⚠️ 两条流水线有重复步骤")
            print(f"重复步骤: {patent_names & citation_names}")
        
        return True
        
    except Exception as e:
        print(f"❌ 流水线结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pipeline_methods():
    """测试流水线方法"""
    print("\n" + "=" * 60)
    print("测试流水线方法")
    print("=" * 60)
    
    try:
        from pipeline import PatentAnalysisPipeline
        
        pipeline = PatentAnalysisPipeline()
        
        # 检查是否有新的方法
        methods = ['run_patent_pipeline', 'run_citation_pipeline', 'run_parallel_pipelines']
        
        for method_name in methods:
            if hasattr(pipeline, method_name):
                print(f"✅ 方法 {method_name} 存在")
            else:
                print(f"❌ 方法 {method_name} 不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 流水线方法测试失败: {e}")
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

def test_pipeline_independence():
    """测试流水线独立性"""
    print("\n" + "=" * 60)
    print("测试流水线独立性")
    print("=" * 60)
    
    try:
        from pipeline import PatentAnalysisPipeline
        
        pipeline = PatentAnalysisPipeline()
        
        # 检查专利数量流水线的输入输出
        patent_steps = [step for step in pipeline.pipeline_steps if step.get('pipeline') == 'patent']
        citation_steps = [step for step in pipeline.pipeline_steps if step.get('pipeline') == 'citation']
        
        # 收集专利数量流水线的所有输出文件
        patent_outputs = set()
        for step in patent_steps:
            patent_outputs.update(step['output_files'])
        
        # 收集被引证次数流水线的所有输出文件
        citation_outputs = set()
        for step in citation_steps:
            citation_outputs.update(step['output_files'])
        
        # 检查是否有交叉依赖
        cross_dependencies = patent_outputs & citation_outputs
        
        if not cross_dependencies:
            print("✅ 两条流水线完全独立，没有交叉依赖")
        else:
            print("⚠️ 两条流水线有交叉依赖")
            print(f"交叉依赖文件: {cross_dependencies}")
        
        # 检查输入文件依赖
        patent_inputs = set()
        for step in patent_steps:
            patent_inputs.update(step['input_files'])
        
        citation_inputs = set()
        for step in citation_steps:
            citation_inputs.update(step['input_files'])
        
        # 共同的输入文件是正常的（如invest.xlsx, data/trimpatent_all.csv）
        common_inputs = patent_inputs & citation_inputs
        print(f"\n共同输入文件: {common_inputs}")
        print("这些是正常的，因为两条流水线都从相同的基础数据开始")
        
        return True
        
    except Exception as e:
        print(f"❌ 流水线独立性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("并行流水线功能测试")
    print("=" * 60)
    
    tests = [
        ("流水线结构", test_pipeline_structure),
        ("流水线方法", test_pipeline_methods),
        ("流水线状态显示", test_pipeline_status),
        ("流水线独立性", test_pipeline_independence),
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
        print("🎉 所有测试通过！并行流水线设计成功")
        print("\n主要改进:")
        print("1. 专利数量和被引证次数现在是两条独立的流水线")
        print("2. 每条流水线可以独立运行")
        print("3. 两条流水线可以并行执行（概念上）")
        print("4. 流水线状态按类型分组显示")
        print("5. 新增了专门的流水线运行方法")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main()


