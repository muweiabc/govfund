# 专利搜索爬虫程序

这个程序可以模拟在CNIPA专利搜索系统中提交搜索命令并获取搜索结果。

## 功能

- 自动访问 https://pss-system.cponline.cnipa.gov.cn/commandSearch
- 提交搜索命令 "SS PA=(航天智造科技股份有限公司)"
- 提取搜索结果并保存到Excel文件

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方法1: 使用简化版本（推荐）

```bash
python patent_scraper_simple.py
```

### 方法2: 使用完整版本

```bash
python patent_scraper.py
```

## 程序特点

1. **自动驱动管理**: 使用webdriver-manager自动下载和管理Chrome驱动
2. **智能元素查找**: 尝试多种CSS选择器来定位页面元素
3. **错误处理**: 包含完善的错误处理和调试信息
4. **结果保存**: 自动将搜索结果保存为Excel文件

## 输出文件

- `patent_search_航天智造科技股份有限公司.xlsx`: 搜索结果
- `page_source.html`: 页面源码（用于调试）
- `search_results_page.html`: 搜索结果页面源码（用于调试）

## 注意事项

1. 确保已安装Chrome浏览器
2. 程序运行时会打开Chrome浏览器窗口
3. 如果遇到反爬虫机制，可能需要调整等待时间
4. 建议在网络稳定的环境下运行

## 自定义搜索

要搜索其他公司，可以修改代码中的 `company_name` 变量：

```python
company_name = "你的公司名称"
```

## 故障排除

如果程序无法正常运行：

1. 检查Chrome浏览器是否已安装
2. 确认网络连接正常
3. 查看生成的调试文件（page_source.html）
4. 调整等待时间参数
