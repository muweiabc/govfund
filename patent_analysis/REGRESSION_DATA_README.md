# 回归数据创建工具使用说明

## 概述

本工具用于创建用于回归分析的面板数据，从投资事件数据中提取公司、年份、省份、treatment等信息，并将每个投资事件扩展为前三年和后三年的6行数据。

## 主要功能

### 1. 基础回归面板数据 (`create_regression_data.py`)
- 从 `invest.xlsx` 读取投资事件数据
- 将每个投资事件扩展为前3年和后3年的6行数据
- 创建DID分析所需的基础变量

### 2. 增强回归面板数据 (`create_enhanced_regression_data.py`)
- 包含基础面板数据的所有功能
- 添加专利数据（专利数量、被引证次数、发明数量等）
- 添加控制变量（GDP、城镇化率、固定资产投资等）
- 创建虚拟变量（省份、投资阶段、年份）

## 数据结构

### 输入数据
- **投资数据**: `invest.xlsx` 中的"有专利公司首次投资"工作表
- **专利数据**: `patent_analysis/company_patent_yearly.xlsx`
- **控制变量数据**: GDP、城镇化率、固定资产投资、就业数据等

### 输出数据
每个投资事件被扩展为6行数据：
- **前3年**: 投资前3年、前2年、前1年
- **投资当年**: 投资发生的年份
- **后3年**: 投资后1年、后2年、后3年

## 使用方法

### 方法1: 使用VS Code调试配置

1. 在VS Code中按 `F5`
2. 选择以下配置之一：
   - **创建回归面板数据**: 创建基础面板数据
   - **创建增强回归面板数据**: 创建包含专利和控制变量的面板数据

### 方法2: 命令行运行

```bash
# 创建基础回归面板数据
python patent_analysis/create_regression_data.py \
    --input_file invest.xlsx \
    --sheet_name "有专利公司首次投资" \
    --output_file patent_analysis/regression_panel_data.xlsx \
    --analyze

# 创建增强回归面板数据
python patent_analysis/create_enhanced_regression_data.py \
    --input_file invest.xlsx \
    --sheet_name "有专利公司首次投资" \
    --patent_file patent_analysis/company_patent_yearly.xlsx \
    --output_file patent_analysis/enhanced_regression_panel_data.xlsx
```

## 输出文件说明

### 基础面板数据 (`regression_panel_data.xlsx`)
包含以下工作表：
- **面板数据**: 主要的面板数据
- **分组统计**: 按treatment和post分组的统计
- **省份统计**: 各省份的观测值数量
- **投资阶段统计**: 各投资阶段的观测值数量
- **投资事件摘要**: 原始投资事件的摘要

### 增强面板数据 (`enhanced_regression_panel_data.xlsx`)
包含以下工作表：
- **面板数据**: 包含所有变量的面板数据
- **数据描述**: 所有变量的描述性统计
- **专利数据统计**: 专利相关变量的统计
- **控制变量统计**: 控制变量的统计
- **分组统计**: 按treatment和post分组的详细统计

## 数据变量说明

### 基础变量
- `company`: 公司名称
- `year`: 观测年份
- `investment_year`: 投资年份
- `treatment`: 处理组标识（0=控制组，1=处理组）
- `post`: 投资后标识（0=投资前，1=投资后）
- `province`: 省份
- `investment_stage`: 投资阶段
- `year_offset`: 相对于投资年份的偏移（-3到+3）
- `period`: 时期描述（前3年、前2年等）
- `time_to_investment`: 到投资的时间距离
- `is_treatment`: 处理组标识
- `is_post_treatment`: 处理组×投资后交互项

### 专利变量（增强版本）
- `patent_count`: 专利数量
- `citation_count`: 被引证次数
- `invention_count`: 发明数量
- `invention_citation`: 发明被引证次数
- `ln_patent_count_plus_1`: ln(专利数量+1)
- `ln_citation_count_plus_1`: ln(被引证次数+1)
- `ln_invention_count_plus_1`: ln(发明数量+1)
- `ln_invention_citation_plus_1`: ln(发明被引证次数+1)

### 控制变量（增强版本）
- `gdp`: 地区生产总值
- `ln_gdp`: ln(GDP+1)
- `urban_rate`: 城镇化率
- `ln_urban_rate`: ln(城镇化率+1)
- `fixed_investment`: 固定资产投资
- `ln_fixed_investment`: ln(固定资产投资+1)
- `secondary_industry_ratio`: 第二产业比例
- `secondary_employment_ratio`: 第二产业就业比例

### 虚拟变量（增强版本）
- `province_*`: 省份虚拟变量
- `stage_*`: 投资阶段虚拟变量
- `year_*`: 年份虚拟变量

## 数据统计示例

### 基础面板数据统计
- **总观测值**: 38,920
- **公司数**: 5,560
- **年份范围**: 1997-2024
- **投资年份范围**: 2000-2021
- **Treatment分布**: 控制组3,928家公司，处理组1,632家公司

### 分组统计
| Treatment | Post | 观测值数 |
|-----------|------|----------|
| 0         | 0    | 11,784   |
| 0         | 1    | 15,712   |
| 1         | 0    | 4,896    |
| 1         | 1    | 6,528    |

## 注意事项

1. **数据匹配**: 专利数据和控制变量的匹配基于公司名称和年份，确保数据质量
2. **缺失值处理**: 对于缺失的专利数据，使用0填充；对于缺失的控制变量，使用0填充
3. **对数变换**: 对专利数据和控制变量进行对数变换，避免异方差问题
4. **虚拟变量**: 自动创建省份、投资阶段、年份的虚拟变量，便于回归分析

## 故障排除

### 常见问题

1. **文件未找到错误**
   - 检查输入文件路径是否正确
   - 确保所有依赖的数据文件存在

2. **数据匹配率低**
   - 检查公司名称是否一致
   - 检查年份范围是否匹配

3. **内存不足**
   - 减少数据量或增加系统内存
   - 使用分块处理

### 调试技巧

1. 使用 `--analyze` 参数获取详细分析
2. 检查输出文件中的统计信息
3. 验证数据匹配情况
4. 检查变量分布是否合理

## 扩展功能

### 添加新的控制变量
1. 在 `load_control_variables()` 函数中添加新的数据源
2. 在 `add_control_variables()` 函数中添加匹配逻辑
3. 更新输出文件的工作表

### 修改时间窗口
1. 修改 `year_offset` 的范围（当前为-3到+3）
2. 调整 `period` 变量的生成逻辑
3. 更新相关的统计和描述

## 联系支持

如有问题，请检查：
1. 输入数据格式是否正确
2. 文件路径是否正确
3. 依赖包是否已安装
4. 系统资源是否充足
