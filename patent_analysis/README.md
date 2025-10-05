# 数据流程

## 概述
按陈蓉博士论文第6章
投资事件发生在2005-2021之间，这样前后三年是2002-2024，因为很多表数据2024年没有

### processinvest.py合并2000-2021年的投资事件，去掉融资主体为“不披露”的，保存到`invest.xlsx`中

### processfund.py 合并下载的政府引导基金数据，保存到`govfund_filtered.xlsx`文件

### company_patent_analysis.py 读取trimpatent_all，按公司和年份统计输出到`company_patent.yearly`

### patent_analysis/create_regression_data.py 读取`invest.xlsx`,提取投资年份，从 `company_patent_yearly.xlsx`获得投资前后三年的专利数，输出为`regress_panel_data.xlsx` （所有面板数据)和 `regression_data_location`(有投资机构属地的面板数据)

### regress.py 读取`regress_panel_data`，生成面板数据和treatment_post，调用panelols进行回归，可配置时间固定效应和个体固定效应

数据范围：
就业人口：2000-2023
省份年份投资统计：2000-2021
地市外商投资：1996-2023
分省城镇化：2000-2003
分省固定资产投资 2003-2023
各产业从业人数 1952-2003
gdp:1952-2024