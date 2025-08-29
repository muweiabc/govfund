# 专利被引证次数分析工具

## 功能描述

本工具用于分析公司专利的被引证次数，具体功能包括：

1. **数据读取**：读取 `data/trimpatent_all.csv` 专利数据文件
2. **公司筛选**：筛选出申请人在 `invest.xlsx` 融资主体列表中的专利
3. **年度统计**：按年计算每个公司的专利被引证次数
4. **结果输出**：生成年度被引证次数矩阵和统计报告

## 文件说明

### 核心文件

- `company_patent_citation_analysis.py` - 主要的分析模块，包含所有核心功能
- `run_citation_analysis.py` - 简化的运行脚本，用于快速执行分析

### 输出文件

- `company_patent_citations_yearly.xlsx` - Excel格式的年度被引证次数矩阵
- `company_patent_citations_matrix.pkl` - Python pickle格式的数据对象

## 使用方法

### 方法1：直接运行分析模块

```python
from company_patent_citation_analysis import analyze_company_patent_citations

# 运行完整分析
sparse_matrix, company_names, years = analyze_company_patent_citations()
```

### 方法2：使用运行脚本

```bash
cd patent_analysis
python run_citation_analysis.py
```

### 方法3：查询特定公司

```python
from company_patent_citation_analysis import query_company_citations

# 查询特定公司的被引证情况
citations = query_company_citations("公司名称")
```

### 方法4：获取被引证最多的公司

```python
from company_patent_citation_analysis import get_top_cited_companies

# 获取被引证次数最多的前10家公司
top_companies = get_top_cited_companies(10)
```

## 数据要求

### 输入文件

1. **invest.xlsx** - 必须包含 "融资主体" 列
2. **data/trimpatent_all.csv** - 必须包含以下列：
   - 申请人
   - 申请年份
   - 被引证次数（或包含"被引证"、"引证"关键词的列）

### 数据格式

- 申请年份：数字格式（如：2020）
- 被引证次数：数字格式（如：5）
- 申请人：文本格式

## 输出结果

### 年度被引证次数矩阵

- 行：公司名称
- 列：年份
- 值：该年该公司的专利被引证次数总和

### 统计信息

- 公司数量
- 年份范围
- 数据稀疏度
- 示例数据展示

## 技术特点

1. **内存优化**：使用分块读取处理大文件
2. **编码兼容**：自动尝试UTF-8和GBK编码
3. **稀疏矩阵**：使用scipy稀疏矩阵节省内存
4. **错误处理**：完善的异常处理和用户提示
5. **进度显示**：使用tqdm显示处理进度

## 注意事项

1. 确保数据文件路径正确
2. 大文件处理可能需要较长时间
3. 建议在分析前备份原始数据
4. 如果遇到编码问题，程序会自动尝试不同编码

## 依赖包

```bash
pip install pandas numpy scipy tqdm openpyxl
```

## 示例输出

```
开始分析公司专利被引证次数...
正在读取invest.xlsx...
共读取到 1500 家融资主体公司
正在读取data/trimpatent_all.csv...
文件大小: 2.50 GB
正在读取专利数据: 100%|██████████| 25/25 [02:30<00:00,  6.00s/it]
专利数据总行数: 2500000
正在预处理数据...
专利申请年份范围: 1985 - 2023
正在筛选融资主体公司的专利...
融资主体公司专利数量: 125000
正在计算每年的被引证次数...
正在构建稀疏矩阵数据: 100%|██████████| 50000/50000 [00:30<00:00, 1666.67it/s]
正在构建稀疏矩阵...
正在保存结果...

=== 分析结果 ===
公司数量: 1500
年份数量: 39
稀疏矩阵形状: (1500, 39)
非零元素数量: 45000
稀疏度: 92.31%

=== 示例数据 ===
前5家公司的被引证情况:
公司A: 总计被引证 150 次
  有专利的年份: {2018: 25, 2019: 30, 2020: 35, 2021: 40, 2022: 20}
公司B: 总计被引证 200 次
  有专利的年份: {2017: 20, 2018: 30, 2019: 40, 2020: 50, 2021: 60}
...

分析完成！
结果已保存到:
- company_patent_citations_matrix.pkl (稀疏矩阵)
- company_patent_citations_yearly.xlsx (Excel格式)
```

## 故障排除

### 常见问题

1. **文件不存在错误**
   - 检查文件路径是否正确
   - 确保文件在指定位置

2. **编码错误**
   - 程序会自动尝试不同编码
   - 如果仍有问题，检查原始文件编码

3. **内存不足**
   - 减小chunk_size参数
   - 关闭其他程序释放内存

4. **列名不匹配**
   - 检查CSV文件的列名
   - 确保包含必要的列

### 联系支持

如果遇到其他问题，请检查：
1. Python版本（建议3.7+）
2. 依赖包版本
3. 数据文件格式
4. 系统内存大小

