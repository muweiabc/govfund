# 数据流程

## 概述
按陈蓉博士论文第6章
投资事件发生在2005-2021之间，这样前后三年是2002-2024，因为很多表数据2024年没有

### processinvest.py合并2000-2021年的投资事件，去掉融资主体为“不披露”的，保存到`invest.xlsx`中

### processfund.py 合并下载的政府引导基金数据，保存到`govfund_filtered.xlsx`文件

### company_patent_analysis.py 读取trimpatent_all，按公司和年份统计输出到`company_patent.yearly`

### preparedata.py 读取`invest.xlsx`,提取投资年份，从 `company_patent_yearly.xlsx`获得投资前后三年的专利数，输出为`regress_data.xlsx`

### did.py 读取`regress_data`，生成面板数据和treatment_post，调用panelols进行回归，可配置时间固定效应和个体固定效应


