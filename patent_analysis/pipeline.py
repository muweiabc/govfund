#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专利分析完整流水线
将company_patent_analysis、company_citation_analysis、preparedata、addgdp和did串联起来
前一个文件的输出作为下一个文件的输入
"""

import os
import sys
import time
import pandas as pd
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class PatentAnalysisPipeline:
    """专利分析流水线类"""
    
    def __init__(self, base_dir='.'):
        """
        初始化流水线
        
        参数:
        base_dir: 基础目录路径
        """
        self.base_dir = base_dir
        self.pipeline_log = []
        self.start_time = time.time()
        
        # 流水线步骤配置 - 两条并行流程
        self.pipeline_steps = [
            # 专利数量流水线 (Patent Pipeline)
            {
                'name': '专利数量分析',
                'function': self.step_patent_analysis,
                'input_files': ['invest.xlsx', 'data/trimpatent_all.csv'],
                'output_files': ['patent_analysis/company_patent_yearly.xlsx'],
                'description': '分析公司专利数量年度数据',
                'pipeline': 'patent'
            },
            {
                'name': '专利数量回归数据准备',
                'function': self.step_prepare_patent_data,
                'input_files': ['invest.xlsx', 'patent_analysis/company_patent_yearly.xlsx'],
                'output_files': ['patent_analysis/regress_data_patents.xlsx'],
                'description': '准备专利数量回归分析数据',
                'pipeline': 'patent'
            },
            {
                'name': '专利数量数据添加省份信息',
                'function': self.step_add_province_patents,
                'input_files': ['invest.xlsx', 'patent_analysis/regress_data_patents.xlsx'],
                'output_files': ['patent_analysis/regress_data_patents_with_province.xlsx'],
                'description': '为专利数量数据添加省份信息',
                'pipeline': 'patent'
            },
            {
                'name': '专利数量数据添加GDP数据',
                'function': self.step_add_gdp_patents,
                'input_files': ['gdp.xlsx', 'patent_analysis/regress_data_patents_with_province.xlsx'],
                'output_files': ['patent_analysis/regress_data_patents_with_gdp.xlsx'],
                'description': '为专利数量数据添加GDP控制变量',
                'pipeline': 'patent'
            },
            {
                'name': '专利数量DID回归分析',
                'function': self.step_did_regression_patents,
                'input_files': ['patent_analysis/regress_data_patents_with_gdp.xlsx'],
                'output_files': ['patent_analysis/did_panel_data_patents_with_year_dummies.xlsx'],
                'description': '执行专利数量DID回归分析',
                'pipeline': 'patent'
            },
            
            # 被引证次数流水线 (Citation Pipeline)
            {
                'name': '被引证次数分析',
                'function': self.step_citation_analysis,
                'input_files': ['invest.xlsx', 'data/trimpatent_all.csv'],
                'output_files': ['patent_analysis/company_patent_citations_yearly.xlsx'],
                'description': '分析公司专利被引证次数年度数据',
                'pipeline': 'citation'
            },
            {
                'name': '被引证次数回归数据准备',
                'function': self.step_prepare_citation_data,
                'input_files': ['invest.xlsx', 'patent_analysis/company_patent_citations_yearly.xlsx'],
                'output_files': ['patent_analysis/regress_data_citations.xlsx'],
                'description': '准备被引证次数回归分析数据',
                'pipeline': 'citation'
            },
            {
                'name': '被引证次数数据添加省份信息',
                'function': self.step_add_province_citations,
                'input_files': ['invest.xlsx', 'patent_analysis/regress_data_citations.xlsx'],
                'output_files': ['patent_analysis/regress_data_citations_with_province.xlsx'],
                'description': '为被引证次数数据添加省份信息',
                'pipeline': 'citation'
            },
            {
                'name': '被引证次数数据添加GDP数据',
                'function': self.step_add_gdp_citations,
                'input_files': ['gdp.xlsx', 'patent_analysis/regress_data_citations_with_province.xlsx'],
                'output_files': ['patent_analysis/regress_data_citations_with_gdp.xlsx'],
                'description': '为被引证次数数据添加GDP控制变量',
                'pipeline': 'citation'
            },
            {
                'name': '被引证次数DID回归分析',
                'function': self.step_did_regression_citations,
                'input_files': ['patent_analysis/regress_data_citations_with_gdp.xlsx'],
                'output_files': ['patent_analysis/did_panel_data_citations_with_year_dummies.xlsx'],
                'description': '执行被引证次数DID回归分析',
                'pipeline': 'citation'
            }
        ]
    
    def log_step(self, step_name, status, message, duration=None):
        """记录流水线步骤执行情况"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'step': step_name,
            'status': status,
            'message': message,
            'duration': duration
        }
        self.pipeline_log.append(log_entry)
        
        # 打印日志
        status_icon = "✅" if status == "成功" else "❌" if status == "失败" else "⚠️"
        print(f"{status_icon} {step_name}: {message}")
        if duration:
            print(f"   耗时: {duration:.2f}秒")
    
    def check_files_exist(self, file_list):
        """检查文件是否存在"""
        missing_files = []
        for file_path in file_list:
            full_path = os.path.join(self.base_dir, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        return missing_files
    
    def step_patent_analysis(self):
        """步骤1: 专利数量分析"""
        try:
            from company_patent_analysis import analyze_company_patents
            
            print("\n" + "="*60)
            print("步骤1: 专利数量分析")
            print("="*60)
            
            result = analyze_company_patents()
            
            if result and result[0] is not None:
                return True, "专利数量分析完成"
            else:
                return False, "专利数量分析失败"
                
        except Exception as e:
            return False, f"专利数量分析出错: {str(e)}"
    
    def step_citation_analysis(self):
        """步骤2: 被引证次数分析"""
        try:
            from company_patent_citation_analysis import analyze_company_patent_citations
            
            print("\n" + "="*60)
            print("步骤2: 被引证次数分析")
            print("="*60)
            
            result = analyze_company_patent_citations()
            
            if result and result[0] is not None:
                return True, "被引证次数分析完成"
            else:
                return False, "被引证次数分析失败"
                
        except Exception as e:
            return False, f"被引证次数分析出错: {str(e)}"
    
    def step_prepare_patent_data(self):
        """步骤3: 专利数量回归数据准备"""
        try:
            from preparedata import extract_regress_data_patents
            
            print("\n" + "="*60)
            print("步骤3: 专利数量回归数据准备")
            print("="*60)
            
            result = extract_regress_data_patents()
            
            if result:
                return True, f"专利数量回归数据准备完成，输出文件: {result['excel_file']}"
            else:
                return False, "专利数量回归数据准备失败"
                
        except Exception as e:
            return False, f"专利数量回归数据准备出错: {str(e)}"
    
    def step_prepare_citation_data(self):
        """步骤4: 被引证次数回归数据准备"""
        try:
            from preparedata import extract_regress_data_citations
            
            print("\n" + "="*60)
            print("步骤4: 被引证次数回归数据准备")
            print("="*60)
            
            result = extract_regress_data_citations()
            
            if result:
                return True, f"被引证次数回归数据准备完成，输出文件: {result['excel_file']}"
            else:
                return False, "被引证次数回归数据准备失败"
                
        except Exception as e:
            return False, f"被引证次数回归数据准备出错: {str(e)}"
    
    def step_add_province_patents(self):
        """步骤5: 专利数量数据添加省份信息"""
        try:
            from add_gdp import extract_province_from_region
            
            print("\n" + "="*60)
            print("步骤5: 专利数量数据添加省份信息")
            print("="*60)
            
            result = extract_province_from_region(
                input_file='patent_analysis/regress_data_patents.xlsx',
                output_file='patent_analysis/regress_data_patents_with_province.xlsx'
            )
            
            if result:
                return True, f"专利数量数据省份信息添加完成，输出文件: {result['excel_file']}"
            else:
                return False, "专利数量数据省份信息添加失败"
                
        except Exception as e:
            return False, f"专利数量数据省份信息添加出错: {str(e)}"
    
    def step_add_province_citations(self):
        """步骤6: 被引证次数数据添加省份信息"""
        try:
            from add_gdp import extract_province_from_region
            
            print("\n" + "="*60)
            print("步骤6: 被引证次数数据添加省份信息")
            print("="*60)
            
            result = extract_province_from_region(
                input_file='patent_analysis/regress_data_citations.xlsx',
                output_file='patent_analysis/regress_data_citations_with_province.xlsx'
            )
            
            if result:
                return True, f"被引证次数数据省份信息添加完成，输出文件: {result['excel_file']}"
            else:
                return False, "被引证次数数据省份信息添加失败"
                
        except Exception as e:
            return False, f"被引证次数数据省份信息添加出错: {str(e)}"
    
    def step_add_gdp_patents(self):
        """步骤7: 专利数量数据添加GDP数据"""
        try:
            from add_gdp import add_province_gdp_data
            
            print("\n" + "="*60)
            print("步骤7: 专利数量数据添加GDP数据")
            print("="*60)
            
            result = add_province_gdp_data(
                input_file='patent_analysis/regress_data_patents_with_province.xlsx',
                output_file='patent_analysis/regress_data_patents_with_gdp.xlsx'
            )
            
            if result:
                return True, f"专利数量数据GDP添加完成，输出文件: {result['excel_file']}"
            else:
                return False, "专利数量数据GDP添加失败"
                
        except Exception as e:
            return False, f"专利数量数据GDP添加出错: {str(e)}"
    
    def step_add_gdp_citations(self):
        """步骤8: 被引证次数数据添加GDP数据"""
        try:
            from add_gdp import add_province_gdp_data
            
            print("\n" + "="*60)
            print("步骤8: 被引证次数数据添加GDP数据")
            print("="*60)
            
            result = add_province_gdp_data(
                input_file='patent_analysis/regress_data_citations_with_province.xlsx',
                output_file='patent_analysis/regress_data_citations_with_gdp.xlsx'
            )
            
            if result:
                return True, f"被引证次数数据GDP添加完成，输出文件: {result['excel_file']}"
            else:
                return False, "被引证次数数据GDP添加失败"
                
        except Exception as e:
            return False, f"被引证次数数据GDP添加出错: {str(e)}"
    
    def step_did_regression_patents(self):
        """步骤9: 专利数量DID回归分析"""
        try:
            from did import perform_did_regression_with_year_dummies
            
            print("\n" + "="*60)
            print("步骤9: 专利数量DID回归分析")
            print("="*60)
            
            result = perform_did_regression_with_year_dummies(
                input_file='patent_analysis/regress_data_patents_with_gdp.xlsx',
                output_file='patent_analysis/did_panel_data_patents_with_year_dummies.xlsx'
            )
            
            if result:
                return True, f"专利数量DID回归分析完成，输出文件: {result['panel_file']}"
            else:
                return False, "专利数量DID回归分析失败"
                
        except Exception as e:
            return False, f"专利数量DID回归分析出错: {str(e)}"
    
    def step_did_regression_citations(self):
        """步骤10: 被引证次数DID回归分析"""
        try:
            from did import perform_did_regression_with_year_dummies
            
            print("\n" + "="*60)
            print("步骤10: 被引证次数DID回归分析")
            print("="*60)
            
            result = perform_did_regression_with_year_dummies(
                input_file='patent_analysis/regress_data_citations_with_gdp.xlsx',
                output_file='patent_analysis/did_panel_data_citations_with_year_dummies.xlsx'
            )
            
            if result:
                return True, f"被引证次数DID回归分析完成，输出文件: {result['panel_file']}"
            else:
                return False, "被引证次数DID回归分析失败"
                
        except Exception as e:
            return False, f"被引证次数DID回归分析出错: {str(e)}"
    
    def run_pipeline(self, start_step=0, end_step=None):
        """
        运行完整流水线
        
        参数:
        start_step: 开始步骤索引（从0开始）
        end_step: 结束步骤索引（不包含），如果为None则运行到最后
        """
        print("="*80)
        print("专利分析完整流水线启动")
        print("="*80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"基础目录: {self.base_dir}")
        
        if end_step is None:
            end_step = len(self.pipeline_steps)
        
        print(f"执行步骤: {start_step} - {end_step-1} (共{end_step-start_step}步)")
        print("="*80)
        
        success_count = 0
        total_steps = end_step - start_step
        
        for step_idx in range(start_step, end_step):
            step = self.pipeline_steps[step_idx]
            step_name = step['name']
            step_description = step['description']
            
            print(f"\n{'='*20} 步骤 {step_idx+1}/{total_steps}: {step_name} {'='*20}")
            print(f"描述: {step_description}")
            
            # 检查输入文件
            missing_files = self.check_files_exist(step['input_files'])
            if missing_files:
                error_msg = f"缺少输入文件: {missing_files}"
                self.log_step(step_name, "失败", error_msg)
                print(f"❌ 步骤失败，跳过后续步骤")
                break
            
            # 执行步骤
            step_start_time = time.time()
            try:
                success, message = step['function']()
                step_duration = time.time() - step_start_time
                
                if success:
                    self.log_step(step_name, "成功", message, step_duration)
                    success_count += 1
                else:
                    self.log_step(step_name, "失败", message, step_duration)
                    print(f"❌ 步骤失败，跳过后续步骤")
                    break
                    
            except Exception as e:
                step_duration = time.time() - step_start_time
                error_msg = f"执行出错: {str(e)}"
                self.log_step(step_name, "失败", error_msg, step_duration)
                print(f"❌ 步骤失败，跳过后续步骤")
                break
        
        # 流水线完成
        total_duration = time.time() - self.start_time
        print("\n" + "="*80)
        print("流水线执行完成")
        print("="*80)
        print(f"成功步骤: {success_count}/{total_steps}")
        print(f"总耗时: {total_duration:.2f}秒")
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存执行日志
        self.save_pipeline_log()
        
        return success_count == total_steps
    
    def save_pipeline_log(self):
        """保存流水线执行日志"""
        log_file = os.path.join(self.base_dir, 'patent_analysis', 'pipeline_log.xlsx')
        
        try:
            log_df = pd.DataFrame(self.pipeline_log)
            log_df.to_excel(log_file, index=False, sheet_name='流水线执行日志')
            print(f"执行日志已保存: {log_file}")
        except Exception as e:
            print(f"保存执行日志失败: {e}")
    
    def run_specific_steps(self, step_names):
        """
        运行指定的步骤
        
        参数:
        step_names: 步骤名称列表
        """
        step_indices = []
        for step_name in step_names:
            for i, step in enumerate(self.pipeline_steps):
                if step['name'] == step_name:
                    step_indices.append(i)
                    break
        
        if not step_indices:
            print("❌ 未找到指定的步骤")
            return False
        
        step_indices.sort()
        start_step = step_indices[0]
        end_step = step_indices[-1] + 1
        
        return self.run_pipeline(start_step, end_step)
    
    def run_patent_pipeline(self):
        """
        运行专利数量流水线
        """
        print("="*80)
        print("专利数量流水线启动")
        print("="*80)
        
        patent_steps = [step for step in self.pipeline_steps if step.get('pipeline') == 'patent']
        if not patent_steps:
            print("❌ 未找到专利数量流水线步骤")
            return False
        
        print(f"专利数量流水线包含 {len(patent_steps)} 个步骤:")
        for i, step in enumerate(patent_steps):
            print(f"  {i+1}. {step['name']}")
        
        # 获取专利数量流水线的步骤索引
        patent_indices = []
        for step in patent_steps:
            for i, pipeline_step in enumerate(self.pipeline_steps):
                if pipeline_step['name'] == step['name']:
                    patent_indices.append(i)
                    break
        
        if not patent_indices:
            print("❌ 无法确定专利数量流水线步骤索引")
            return False
        
        patent_indices.sort()
        start_step = patent_indices[0]
        end_step = patent_indices[-1] + 1
        
        return self.run_pipeline(start_step, end_step)
    
    def run_citation_pipeline(self):
        """
        运行被引证次数流水线
        """
        print("="*80)
        print("被引证次数流水线启动")
        print("="*80)
        
        citation_steps = [step for step in self.pipeline_steps if step.get('pipeline') == 'citation']
        if not citation_steps:
            print("❌ 未找到被引证次数流水线步骤")
            return False
        
        print(f"被引证次数流水线包含 {len(citation_steps)} 个步骤:")
        for i, step in enumerate(citation_steps):
            print(f"  {i+1}. {step['name']}")
        
        # 获取被引证次数流水线的步骤索引
        citation_indices = []
        for step in citation_steps:
            for i, pipeline_step in enumerate(self.pipeline_steps):
                if pipeline_step['name'] == step['name']:
                    citation_indices.append(i)
                    break
        
        if not citation_indices:
            print("❌ 无法确定被引证次数流水线步骤索引")
            return False
        
        citation_indices.sort()
        start_step = citation_indices[0]
        end_step = citation_indices[-1] + 1
        
        return self.run_pipeline(start_step, end_step)
    
    def run_parallel_pipelines(self):
        """
        并行运行两条流水线
        注意：这是概念上的并行，实际执行仍然是顺序的
        但两条流水线可以独立运行，互不依赖
        """
        print("="*80)
        print("并行流水线启动")
        print("="*80)
        print("注意：两条流水线将顺序执行，但它们是独立的流程")
        print("专利数量流水线和被引证次数流水线可以独立运行")
        
        # 先运行专利数量流水线
        print("\n" + "="*60)
        print("第一阶段：运行专利数量流水线")
        print("="*60)
        patent_success = self.run_patent_pipeline()
        
        if not patent_success:
            print("❌ 专利数量流水线执行失败")
            return False
        
        # 再运行被引证次数流水线
        print("\n" + "="*60)
        print("第二阶段：运行被引证次数流水线")
        print("="*60)
        citation_success = self.run_citation_pipeline()
        
        if not citation_success:
            print("❌ 被引证次数流水线执行失败")
            return False
        
        print("\n" + "="*80)
        print("🎉 两条流水线都执行成功！")
        print("="*80)
        return True
    
    def show_pipeline_status(self):
        """显示流水线状态"""
        print("="*80)
        print("流水线状态概览")
        print("="*80)
        
        # 按流水线类型分组显示
        patent_steps = [step for step in self.pipeline_steps if step.get('pipeline') == 'patent']
        citation_steps = [step for step in self.pipeline_steps if step.get('pipeline') == 'citation']
        
        # 显示专利数量流水线状态
        print("\n" + "="*60)
        print("专利数量流水线状态")
        print("="*60)
        for i, step in enumerate(patent_steps):
            self._show_step_status(step, i+1, 'patent')
        
        # 显示被引证次数流水线状态
        print("\n" + "="*60)
        print("被引证次数流水线状态")
        print("="*60)
        for i, step in enumerate(citation_steps):
            self._show_step_status(step, i+1, 'citation')
        
        # 显示总体统计
        print("\n" + "="*60)
        print("总体统计")
        print("="*60)
        total_steps = len(self.pipeline_steps)
        completed_steps = sum(1 for step in self.pipeline_steps 
                            if all(os.path.exists(os.path.join(self.base_dir, output_file)) 
                                   for output_file in step['output_files']))
        
        print(f"总步骤数: {total_steps}")
        print(f"已完成步骤: {completed_steps}")
        print(f"完成率: {completed_steps/total_steps*100:.1f}%")
    
    def _show_step_status(self, step, step_num, pipeline_type):
        """显示单个步骤的状态"""
        input_files = step['input_files']
        output_files = step['output_files']
        
        # 检查输入文件状态
        input_status = []
        for input_file in input_files:
            full_path = os.path.join(self.base_dir, input_file)
            if os.path.exists(full_path):
                input_status.append(f"✅ {input_file}")
            else:
                input_status.append(f"❌ {input_file}")
        
        # 检查输出文件状态
        output_status = []
        for output_file in output_files:
            full_path = os.path.join(self.base_dir, output_file)
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path) / (1024*1024)  # MB
                output_status.append(f"✅ {output_file} ({file_size:.1f}MB)")
            else:
                output_status.append(f"❌ {output_file}")
        
        print(f"\n步骤 {step_num}: {step['name']} [{pipeline_type}]")
        print(f"  描述: {step['description']}")
        print(f"  输入文件:")
        for status in input_status:
            print(f"    {status}")
        print(f"  输出文件:")
        for status in output_status:
            print(f"    {status}")


def main():
    """主函数"""
    print("专利分析流水线工具")
    print("="*50)
    
    # 创建流水线实例
    pipeline = PatentAnalysisPipeline()
    
    # 显示流水线状态
    pipeline.show_pipeline_status()
    
    # 询问用户选择
    print("\n请选择执行模式:")
    print("1. 运行完整流水线（串行执行所有步骤）")
    print("2. 运行专利数量流水线")
    print("3. 运行被引证次数流水线")
    print("4. 并行运行两条流水线")
    print("5. 运行指定步骤")
    print("6. 只显示状态")
    
    try:
        choice = input("\n请输入选择 (1/2/3/4/5/6): ").strip()
        
        if choice == '1':
            # 运行完整流水线
            success = pipeline.run_pipeline()
            if success:
                print("\n🎉 完整流水线执行成功！")
            else:
                print("\n⚠️ 完整流水线执行失败，请检查错误信息")
                
        elif choice == '2':
            # 运行专利数量流水线
            success = pipeline.run_patent_pipeline()
            if success:
                print("\n🎉 专利数量流水线执行成功！")
            else:
                print("\n⚠️ 专利数量流水线执行失败，请检查错误信息")
                
        elif choice == '3':
            # 运行被引证次数流水线
            success = pipeline.run_citation_pipeline()
            if success:
                print("\n🎉 被引证次数流水线执行成功！")
            else:
                print("\n⚠️ 被引证次数流水线执行失败，请检查错误信息")
                
        elif choice == '4':
            # 并行运行两条流水线
            success = pipeline.run_parallel_pipelines()
            if success:
                print("\n🎉 两条流水线都执行成功！")
            else:
                print("\n⚠️ 并行流水线执行失败，请检查错误信息")
                
        elif choice == '5':
            # 运行指定步骤
            print("\n可用步骤:")
            for i, step in enumerate(pipeline.pipeline_steps):
                pipeline_type = step.get('pipeline', 'unknown')
                print(f"  {i+1}. {step['name']} [{pipeline_type}]")
            
            step_input = input("\n请输入要执行的步骤编号 (用逗号分隔，如: 1,3,5): ").strip()
            try:
                step_numbers = [int(x.strip()) - 1 for x in step_input.split(',')]
                step_names = [pipeline.pipeline_steps[i]['name'] for i in step_numbers if 0 <= i < len(pipeline.pipeline_steps)]
                
                if step_names:
                    print(f"\n将执行步骤: {', '.join(step_names)}")
                    success = pipeline.run_specific_steps(step_names)
                    if success:
                        print("\n🎉 指定步骤执行成功！")
                    else:
                        print("\n⚠️ 指定步骤执行失败，请检查错误信息")
                else:
                    print("❌ 无效的步骤编号")
            except ValueError:
                print("❌ 输入格式错误")
                
        elif choice == '6':
            print("已显示流水线状态")
            
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
