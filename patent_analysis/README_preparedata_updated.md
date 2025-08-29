# 修改后的preparedata.py功能说明

## 主要改进

### 1. 参数化设计
- `extract_regress_data()` 函数现在接受两个参数：
  - `patent_data_file`: 专利数据文件路径
  - `data_type`: 数据类型（'patent_count' 或 'citation_count'）

### 2. 支持两种数据类型
- **专利数量数据** (`data_type='patent_count'`)
  - 默认文件：`company_patent_yearly.xlsx`
  - 默认sheet：`有专利公司`
  - 输出文件：`regress_data_patents.xlsx`

- **被引证次数数据** (`data_type='citation_count'`)
  - 默认文件：`company_patent_citations_yearly.xlsx`
  - 默认sheet：`被引证次数`
  - 输出文件：`regress_data_citations.xlsx`

### 3. 便捷函数
- `extract_regress_data_patents()`: 专门处理专利数量数据
- `extract_regress_data_citations()`: 专门处理被引证次数数据

## 使用方法

### 方法1：使用便捷函数

```python
from preparedata import extract_regress_data_patents, extract_regress_data_citations

# 处理专利数量数据
result_patents = extract_regress_data_patents()

# 处理被引证次数数据
result_citations = extract_regress_data_citations()
```

### 方法2：使用通用函数

```python
from preparedata import extract_regress_data

# 处理专利数量数据
result_patents = extract_regress_data(
    patent_data_file='company_patent_yearly.xlsx',
    data_type='patent_count'
)

# 处理被引证次数数据
result_citations = extract_regress_data(
    patent_data_file='company_patent_citations_yearly.xlsx',
    data_type='citation_count'
)
```

### 方法3：自定义文件路径

```python
# 处理自定义专利数据文件
result = extract_regress_data(
    patent_data_file='my_patent_data.xlsx',
    data_type='patent_count'
)
```

## 输出文件说明

### 专利数量数据输出 (`regress_data_patents.xlsx`)

**主要数据表：专利数量回归数据**
- 公司名称
- 投资年份
- 投资时间
- treatment
- 前3年专利总数
- 投资当年专利数
- 后3年专利总数
- 前3年专利数_前1年/前2年/前3年
- 后3年专利数_后1年/后2年/后3年
- 专利增长率

**统计表：专利数量数据统计**
- 描述性统计信息

**年份统计：专利数量按年份统计**
- 按投资年份分组的统计信息

### 被引证次数数据输出 (`regress_data_citations.xlsx`)

**主要数据表：被引证次数回归数据**
- 公司名称
- 投资年份
- 投资时间
- treatment
- 前3年被引证总数
- 投资当年被引证数
- 后3年被引证总数
- 前3年被引证数_前1年/前2年/前3年
- 后3年被引证数_后1年/后2年/后3年
- 被引证增长率

**统计表：被引证次数数据统计**
- 描述性统计信息

**年份统计：被引证次数按年份统计**
- 按投资年份分组的统计信息

## 技术特点

### 1. 智能文件识别
- 自动检测公司名称列
- 支持多种列名格式（公司、名称、申请人、Unnamed: 0等）
- 支持索引匹配

### 2. 灵活的数据处理
- 自动处理缺失数据
- 支持不同的Excel sheet名称
- 错误处理和回退机制

### 3. 数据完整性保证
- 确保所有公司都在结果中
- 确保所有年份都在结果中
- 自动填充缺失值为0

## 测试

运行测试脚本验证功能：

```bash
cd patent_analysis
python test_preparedata.py
```

测试内容包括：
1. 专利数量数据处理
2. 被引证次数数据处理（如果文件存在）
3. 自定义数据处理

## 注意事项

1. **文件依赖**：
   - `invest.xlsx` 必须包含 "有专利公司首次投资" sheet
   - 专利数据文件必须包含年份列和公司名称列

2. **数据格式**：
   - 年份列必须是数字格式
   - 公司名称必须与投资数据中的"融资主体"匹配

3. **内存使用**：
   - 大文件处理可能需要较多内存
   - 建议在处理前关闭其他程序

## 示例输出

```
=== 专利数量数据分析 ===
=== 提取投资前后专利时间序列数据 ===
数据类型: patent_count
1. 读取首次投资数据...
   - 首次投资记录数: 1,234
2. 读取专利年度数据...
   - 专利数据文件: company_patent_yearly.xlsx
   - 有专利公司数: 1,100
...

=== 被引证次数数据分析 ===
=== 提取投资前后专利时间序列数据 ===
数据类型: citation_count
1. 读取首次投资数据...
   - 首次投资记录数: 1,234
2. 读取专利年度数据...
   - 专利数据文件: company_patent_citations_yearly.xlsx
   - 有专利公司数: 1,100
...

专利数量分析结果:
  - 文件: regress_data_patents.xlsx
  - 公司数: 1,100
  - 年份范围: 2010 - 2020

被引证次数分析结果:
  - 文件: regress_data_citations.xlsx
  - 公司数: 1,100
  - 年份范围: 2010 - 2020
```

## 故障排除

### 常见问题

1. **文件不存在错误**
   - 检查文件路径是否正确
   - 确保所有依赖文件存在

2. **列名不匹配**
   - 检查Excel文件的列名
   - 确保包含必要的列

3. **数据类型错误**
   - 确保年份列是数字格式
   - 检查专利数据列的数据类型

### 联系支持

如果遇到其他问题，请检查：
1. Python版本（建议3.7+）
2. 依赖包版本（pandas, openpyxl）
3. 数据文件格式
4. 文件编码

