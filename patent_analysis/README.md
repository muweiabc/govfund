# 数据流程

## 概述

### processinvest.py合并2000-2021年的投资事件，去掉融资主体为“不披露”的，保存到`invest.xlsx`中

### processfund.py 合并下载的政府引导基金数据，保存到`govfund_filtered.xlsx`文件

### company_patent_analysis.py 读取trimpatent_all，按公司和年份统计输出到`company_patent.yearly`

### preparedata.py 读取`invest.xlsx`,提取投资年份，从 `company_patent_yearly.xlsx`获得投资前后三年的专利数，输出为`regress_data.xlsx`

### add_gdp.py读取`regress_data.xlsx`, 添加公司所属的省份，从`gdp.xlsx`中找到对应省份和年份（1999-2024）的gdp，添加投资前后三年该省份的gdp数据,输出`regress_data_with_gdp`

### did.py 读取`regress_data_with_gdp`，生成面板数据和treatment_post，调用panelols进行回归，可配置时间固定效应和个体固定效应


