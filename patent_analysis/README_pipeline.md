# 专利分析完整流水线

## 概述

本流水线将专利分析的各个模块串联起来，实现从原始数据到最终DID回归分析的完整流程。前一个文件的输出作为下一个文件的输入，确保数据流的连续性和一致性。

## 流水线步骤

### 步骤1: 专利数量分析
- **输入文件**: `invest.xlsx`, `data/trimpatent_all.csv`
- **输出文件**: `patent_analysis/company_patent_yearly.xlsx`
- **功能**: 分析公司专利数量年度数据
- **模块**: `company_patent_analysis.py`

### 步骤2: 被引证次数分析
- **输入文件**: `invest.xlsx`, `data/trimpatent_all.csv`
- **输出文件**: `patent_analysis/company_patent_citations_yearly.xlsx`
- **功能**: 分析公司专利被引证次数年度数据
- **模块**: `company_patent_citation_analysis.py`

### 步骤3: 专利数量回归数据准备
- **输入文件**: `invest.xlsx`, `patent_analysis/company_patent_yearly.xlsx`
- **输出文件**: `patent_analysis/regress_data_patents.xlsx`
- **功能**: 准备专利数量回归分析数据
- **模块**: `preparedata.py`

### 步骤4: 被引证次数回归数据准备
- **输入文件**: `invest.xlsx`, `patent_analysis/company_patent_citations_yearly.xlsx`
- **输出文件**: `patent_analysis/regress_data_citations.xlsx`
- **功能**: 准备被引证次数回归分析数据
- **模块**: `preparedata.py`

### 步骤5: 添加省份信息
- **输入文件**: `invest.xlsx`, `patent_analysis/regress_data_patents.xlsx`
- **输出文件**: `patent_analysis/regress_data_with_province.xlsx`
- **功能**: 为专利数量数据添加省份信息
- **模块**: `add_gdp.py`

### 步骤6: 添加GDP数据
- **输入文件**: `gdp.xlsx`, `patent_analysis/regress_data_with_province.xlsx`
- **输出文件**: `patent_analysis/regress_data_with_gdp.xlsx`
- **功能**: 为数据添加GDP控制变量
- **模块**: `add_gdp.py`

### 步骤7: DID回归分析
- **输入文件**: `patent_analysis/regress_data_with_gdp.xlsx`
- **输出文件**: `patent_analysis/did_panel_data_with_year_dummies.xlsx`
- **功能**: 执行DID回归分析
- **模块**: `did.py`

## 使用方法

### 方法1: 运行完整流水线

```bash
cd patent_analysis
python pipeline.py
```

选择选项1运行完整流水线。

### 方法2: 运行指定步骤

```bash
cd patent_analysis
python pipeline.py
```

选择选项2，然后输入要执行的步骤编号。

### 方法3: 使用简化测试脚本

```bash
cd patent_analysis
python run_pipeline_simple.py
```

选择不同的测试模式。

### 方法4: 编程方式使用

```python
from pipeline import PatentAnalysisPipeline

# 创建流水线实例
pipeline = PatentAnalysisPipeline()

# 运行完整流水线
success = pipeline.run_pipeline()

# 运行指定步骤
success = pipeline.run_specific_steps(['专利数量分析', '被引证次数分析'])

# 显示流水线状态
pipeline.show_pipeline_status()
```

## 文件依赖关系

```
invest.xlsx
    ↓
data/trimpatent_all.csv
    ↓
company_patent_yearly.xlsx (步骤1输出)
    ↓
regress_data_patents.xlsx (步骤3输出)
    ↓
regress_data_with_province.xlsx (步骤5输出)
    ↓
gdp.xlsx
    ↓
regress_data_with_gdp.xlsx (步骤6输出)
    ↓
did_panel_data_with_year_dummies.xlsx (步骤7输出)
```

## 输出文件说明

### 中间文件
- `company_patent_yearly.xlsx`: 公司年度专利数量矩阵
- `company_patent_citations_yearly.xlsx`: 公司年度专利被引证次数矩阵
- `regress_data_patents.xlsx`: 专利数量回归数据
- `regress_data_citations.xlsx`: 被引证次数回归数据
- `regress_data_with_province.xlsx`: 带省份信息的回归数据
- `regress_data_with_gdp.xlsx`: 带GDP控制变量的回归数据

### 最终输出
- `did_panel_data_with_year_dummies.xlsx`: DID回归分析的面板数据
- `pipeline_log.xlsx`: 流水线执行日志

## 技术特点

### 1. 自动化流程
- 自动检查输入文件是否存在
- 自动执行各个分析步骤
- 自动记录执行日志和耗时

### 2. 错误处理
- 完善的异常处理机制
- 步骤失败时自动停止后续步骤
- 详细的错误信息记录

### 3. 灵活执行
- 支持运行完整流水线
- 支持运行指定步骤
- 支持从任意步骤开始执行

### 4. 状态监控
- 实时显示执行进度
- 文件状态检查
- 执行结果统计

## 注意事项

### 1. 文件要求
- 确保所有输入文件存在且格式正确
- 检查文件路径和权限
- 确保有足够的磁盘空间

### 2. 执行时间
- 完整流水线可能需要较长时间
- 建议在非高峰期执行
- 可以分步骤执行以节省时间

### 3. 内存使用
- 大文件处理可能需要较多内存
- 建议关闭其他程序
- 监控系统资源使用情况

### 4. 错误处理
- 如果某步骤失败，检查错误信息
- 确保输入文件格式正确
- 检查依赖包是否安装完整

## 故障排除

### 常见问题

1. **模块导入失败**
   - 检查Python路径设置
   - 确保所有依赖包已安装
   - 检查文件语法错误

2. **文件不存在错误**
   - 检查文件路径是否正确
   - 确保文件在指定位置
   - 检查文件权限

3. **执行超时**
   - 检查数据文件大小
   - 增加系统内存
   - 分步骤执行

4. **结果文件异常**
   - 检查输入数据质量
   - 验证数据格式
   - 查看执行日志

### 联系支持

如果遇到其他问题，请检查：
1. Python版本（建议3.7+）
2. 依赖包版本
3. 数据文件格式
4. 系统资源情况

## 示例输出

```
================================================================================
专利分析完整流水线启动
================================================================================
开始时间: 2024-01-15 10:30:00
基础目录: .
执行步骤: 0 - 6 (共7步)
================================================================================

==================== 步骤 1/7: 专利数量分析 ====================
描述: 分析公司专利数量年度数据
✅ 专利数量分析: 专利数量分析完成
   耗时: 45.23秒

==================== 步骤 2/7: 被引证次数分析 ====================
描述: 分析公司专利被引证次数年度数据
✅ 被引证次数分析: 被引证次数分析完成
   耗时: 52.18秒

...

================================================================================
流水线执行完成
================================================================================
成功步骤: 7/7
总耗时: 325.67秒
完成时间: 2024-01-15 10:35:25
执行日志已保存: patent_analysis/pipeline_log.xlsx
```

## 扩展功能

### 1. 添加新步骤
在`pipeline_steps`列表中添加新的步骤配置。

### 2. 自定义执行逻辑
继承`PatentAnalysisPipeline`类，重写相关方法。

### 3. 并行执行
修改流水线支持并行执行多个步骤。

### 4. 监控和报告
添加更详细的执行监控和报告功能。

