from hmac import new
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup

def modify_gov_html(html_content,title):
    """
    读取HTML文件，删除第一个表格中的第10到第40行（<tr>标签），
    并在表格末尾添加一行内容为 '1, 2, 3, 4, 5' 的新行。

    :param file_path: HTML 文件路径
    """
    

    # 2. 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'lxml')
    tabletitle = soup.new_tag('p')
    tabletitle.string = title
    soup.insert(0, tabletitle)
    # 3. 找到第一个表格 (假设 statsmodels 的结果是唯一的或第一个表格)
    table = soup.find('table')

    if not table:
        print("错误：HTML 中未找到表格 (<table> 标签)。")
        return

    # 4. 获取所有行 (<tr> 标签)
    rows = table.find_all('tr')

    # 5. 删除第 10 到第 40 行 (Python 索引从 0 开始)
    # 对应实际行号：10, 11, ..., 40
    # 对应 Python 索引：9, 10, ..., 39
    
    # 确定要删除的索引范围
    # 注意：在删除元素时，最好从后往前删除，以避免索引混乱。
    rows[80].decompose()
    # 创建新的一行 <tr> 标签
    new_row = soup.new_tag('tr')
    
    # 内容：1, 2, 3, 4, 5
    data_list = ['控制', '控制', '控制', '控制', '控制'] 
    data_head = soup.new_tag('th')
    data_head.string = '省份固定效应'
    new_row.append(data_head)
    for data in data_list:
        # 创建新的数据单元格 <td> 标签
        new_cell = soup.new_tag('td')
        new_cell.string = data
        # 将单元格添加到新行中
        new_row.append(new_cell)
    table.insert(85, new_row)

    new_row = soup.new_tag('tr')
    data_head = soup.new_tag('th')
    data_head.string = '年份固定效应'
    new_row.append(data_head)
    for data in data_list:
        # 创建新的数据单元格 <td> 标签
        new_cell = soup.new_tag('td')
        new_cell.string = data
        # 将单元格添加到新行中
        new_row.append(new_cell)
    table.insert(86, new_row)

    start_index_to_delete = 15
    end_index_to_delete = 73 # 这个索引对应第 41 行，但不包含在切片中

    # 确保索引在有效范围内
    if len(rows) > start_index_to_delete:
        
        # 批量删除行
        # 我们迭代这个范围内的所有行，并使用 .decompose() 方法从解析树中移除它们
        # 从 end_index_to_delete - 1 倒数到 start_index_to_delete
        for i in range(min(end_index_to_delete, len(rows)) - 1, start_index_to_delete - 1, -1):
            if i < len(rows):
                 rows[i].decompose()
            
        print(f"成功删除表格中索引 {start_index_to_delete} 到 {min(end_index_to_delete, len(rows)) - 1} 之间的行。")
    else:
        print(f"警告：表格总行数不足 {start_index_to_delete + 1} 行，未执行删除操作。")

    return str(soup)
    # return soup.prettify()


def modify_html_main_regress(html_content):
    """
    读取HTML文件，删除第一个表格中的第10到第40行（<tr>标签），
    并在表格末尾添加一行内容为 '1, 2, 3, 4, 5' 的新行。

    :param file_path: HTML 文件路径
    """
    html_content = html_content.replace('二产就业比例', 'SIEP')
    html_content = html_content.replace('城镇化率', 'UrbanizationRate')
    # 2. 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # 3. 找到第一个表格 (假设 statsmodels 的结果是唯一的或第一个表格)
    table = soup.find('table')

    if not table:
        print("错误：HTML 中未找到表格 (<table> 标签)。")
        return

    # 4. 获取所有行 (<tr> 标签)
    rows = table.find_all('tr')

    # 5. 删除第 10 到第 40 行 (Python 索引从 0 开始)
    # 对应实际行号：10, 11, ..., 40
    # 对应 Python 索引：9, 10, ..., 39
    
    # 确定要删除的索引范围
    # 注意：在删除元素时，最好从后往前删除，以避免索引混乱。
    rows[78].decompose()
    # 创建新的一行 <tr> 标签
    new_row = soup.new_tag('tr')
    
    

    start_index_to_delete = 13
    end_index_to_delete = 77 # 这个索引对应第 41 行，但不包含在切片中

    # 确保索引在有效范围内
    if len(rows) > start_index_to_delete:
        
        # 批量删除行
        # 我们迭代这个范围内的所有行，并使用 .decompose() 方法从解析树中移除它们
        # 从 end_index_to_delete - 1 倒数到 start_index_to_delete
        for i in range(76, 58, -1):
            if i < len(rows):
                 rows[i].decompose()
        for i in range(52, 12, -1):
            if i < len(rows):
                 rows[i].decompose()
            
        print(f"成功删除表格中索引 {start_index_to_delete} 到 {min(end_index_to_delete, len(rows)) - 1} 之间的行。")
    else:
        print(f"警告：表格总行数不足 {start_index_to_delete + 1} 行，未执行删除操作。")
    
    # 内容：1, 2, 3, 4, 5
    data_list = ['控制', '控制', '控制', '控制', '控制'] 
    data_head = soup.new_tag('th')
    data_head.string = '省份固定效应'
    new_row.append(data_head)
    for data in data_list:
        # 创建新的数据单元格 <td> 标签
        new_cell = soup.new_tag('td')
        new_cell.string = data
        # 将单元格添加到新行中
        new_row.append(new_cell)
    table.insert(97, new_row)

    new_row = soup.new_tag('tr')
    data_head = soup.new_tag('th')
    data_head.string = '年份固定效应'
    new_row.append(data_head)
    for data in data_list:
        # 创建新的数据单元格 <td> 标签
        new_cell = soup.new_tag('td')
        new_cell.string = data
        # 将单元格添加到新行中
        new_row.append(new_cell)
    table.insert(98, new_row)
    # table.append(new_row)
        
    print("成功在表格末尾添加新的一行：1, 2, 3, 4, 5。")

    return soup.prettify()

def modify_stage_regress(html_content):
    """
    读取HTML文件，删除第一个表格中的第10到第40行（<tr>标签），
    并在表格末尾添加一行内容为 '1, 2, 3, 4, 5' 的新行。

    :param file_path: HTML 文件路径
    """
    html_content = html_content.replace('二产就业比例', 'SIEP')
    html_content = html_content.replace('城镇化率', 'UrbanizationRate')
    # 2. 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # 3. 找到第一个表格 (假设 statsmodels 的结果是唯一的或第一个表格)
    table = soup.find('table')

    if not table:
        print("错误：HTML 中未找到表格 (<table> 标签)。")
        return

    # 4. 获取所有行 (<tr> 标签)
    rows = table.find_all('tr')

    # 5. 删除第 10 到第 40 行 (Python 索引从 0 开始)
    # 对应实际行号：10, 11, ..., 40
    # 对应 Python 索引：9, 10, ..., 39
    
    # 确定要删除的索引范围
    # 注意：在删除元素时，最好从后往前删除，以避免索引混乱。
    rows[14].decompose()
    # 创建新的一行 <tr> 标签
    new_row = soup.new_tag('tr')
    
    # 内容：1, 2, 3, 4, 5
    data_list = ['控制', '控制', '控制', '控制'] 
    data_head = soup.new_tag('th')
    data_head.string = '省份固定效应'
    new_row.append(data_head)
    for data in data_list:
        # 创建新的数据单元格 <td> 标签
        new_cell = soup.new_tag('td')
        new_cell.string = data
        # 将单元格添加到新行中
        new_row.append(new_cell)
    table.insert(29, new_row)

    new_row = soup.new_tag('tr')
    data_head = soup.new_tag('th')
    data_head.string = '年份固定效应'
    new_row.append(data_head)
    for data in data_list:
        # 创建新的数据单元格 <td> 标签
        new_cell = soup.new_tag('td')
        new_cell.string = data
        # 将单元格添加到新行中
        new_row.append(new_cell)
    table.insert(30, new_row)

    start_index_to_delete = 13
    end_index_to_delete = 77 # 这个索引对应第 41 行，但不包含在切片中


     
    # table.append(new_row)
        
    print("成功在表格末尾添加新的一行：1, 2, 3, 4, 5。")

    return soup.prettify()

def modify_same_region(html_content):
    """
    读取HTML文件，删除第一个表格中的第10到第40行（<tr>标签），
    并在表格末尾添加一行内容为 '1, 2, 3, 4, 5' 的新行。

    :param file_path: HTML 文件路径
    """
    html_content = html_content.replace('二产就业比例', 'SIEP')
    html_content = html_content.replace('城镇化率', 'UrbanizationRate')
    # 2. 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # 3. 找到第一个表格 (假设 statsmodels 的结果是唯一的或第一个表格)
    table = soup.find('table')

    if not table:
        print("错误：HTML 中未找到表格 (<table> 标签)。")
        return

    # 4. 获取所有行 (<tr> 标签)
    rows = table.find_all('tr')

    # 5. 删除第 10 到第 40 行 (Python 索引从 0 开始)
    # 对应实际行号：10, 11, ..., 40
    # 对应 Python 索引：9, 10, ..., 39
    
    # 确定要删除的索引范围
    # 注意：在删除元素时，最好从后往前删除，以避免索引混乱。
    rows[18].decompose()
    # 创建新的一行 <tr> 标签
    new_row = soup.new_tag('tr')

    data_list = ['控制', '控制'] 
    new_row = soup.new_tag('tr')
    data_head = soup.new_tag('th')
    data_head.string = '年份固定效应'
    new_row.append(data_head)
    for data in data_list:
        # 创建新的数据单元格 <td> 标签
        new_cell = soup.new_tag('td')
        new_cell.string = data
        # 将单元格添加到新行中
        new_row.append(new_cell)
    table.insert(34, new_row)

        
    print("成功在表格末尾添加新的一行：1, 2, 3, 4, 5。")

    return soup.prettify()

def modify_did_trend(html_content):
    """
    读取HTML文件，删除第一个表格中的第10到第40行（<tr>标签），
    并在表格末尾添加一行内容为 '1, 2, 3, 4, 5' 的新行。

    :param file_path: HTML 文件路径
    """
    html_content = html_content.replace('二产就业比例', 'SIEP')
    html_content = html_content.replace('城镇化率', 'UrbanizationRate')
    # 2. 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # 3. 找到第一个表格 (假设 statsmodels 的结果是唯一的或第一个表格)
    table = soup.find('table')

    if not table:
        print("错误：HTML 中未找到表格 (<table> 标签)。")
        return

    # 4. 获取所有行 (<tr> 标签)
    rows = table.find_all('tr')

    # 5. 删除第 10 到第 40 行 (Python 索引从 0 开始)
    # 对应实际行号：10, 11, ..., 40
    # 对应 Python 索引：9, 10, ..., 39
    
    # 确定要删除的索引范围
    # 注意：在删除元素时，最好从后往前删除，以避免索引混乱。
    rows[38].decompose()
    # 创建新的一行 <tr> 标签
    new_row = soup.new_tag('tr')

    data_list = ['控制', '控制','控制','控制'] 
    new_row = soup.new_tag('tr')
    data_head = soup.new_tag('th')
    data_head.string = '年份固定效应'
    new_row.append(data_head)
    for data in data_list:
        # 创建新的数据单元格 <td> 标签
        new_cell = soup.new_tag('td')
        new_cell.string = data
        # 将单元格添加到新行中
        new_row.append(new_cell)
    table.insert(74, new_row)

        
    print("成功在表格末尾添加新的一行：1, 2, 3, 4, 5。")

    return soup.prettify()


def modify_region_html(html_content):
    """
    读取HTML文件，删除第一个表格中的第10到第40行（<tr>标签），
    并在表格末尾添加一行内容为 '1, 2, 3, 4, 5' 的新行。

    :param file_path: HTML 文件路径
    """
    html_content = html_content.replace('二产就业比例', 'SIEP')
    html_content = html_content.replace('城镇化率', 'UrbanizationRate')
    # 2. 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # 3. 找到第一个表格 (假设 statsmodels 的结果是唯一的或第一个表格)
    table = soup.find('table')

    if not table:
        print("错误：HTML 中未找到表格 (<table> 标签)。")
        return

    # 4. 获取所有行 (<tr> 标签)
    rows = table.find_all('tr')

    # 5. 删除第 10 到第 40 行 (Python 索引从 0 开始)
    # 对应实际行号：10, 11, ..., 40
    # 对应 Python 索引：9, 10, ..., 39
    
    # 确定要删除的索引范围
    # 注意：在删除元素时，最好从后往前删除，以避免索引混乱。
    rows[18].decompose()
    # 创建新的一行 <tr> 标签
    new_row = soup.new_tag('tr')

    data_list = ['控制', '控制', '控制', '控制'] 
    new_row = soup.new_tag('tr')
    data_head = soup.new_tag('th')
    data_head.string = '年份固定效应'
    new_row.append(data_head)
    for data in data_list:
        # 创建新的数据单元格 <td> 标签
        new_cell = soup.new_tag('td')
        new_cell.string = data
        # 将单元格添加到新行中
        new_row.append(new_cell)
    table.insert(34, new_row)

        
    print("成功在表格末尾添加新的一行：1, 2, 3, 4, 5。")

    return soup.prettify()


def add_province_investment():
    first_investments_df = pd.read_excel('invest.xlsx', sheet_name='有专利公司首次投资')
    first_investments_df = first_investments_df[(first_investments_df['投资阶段'] != '--') & (~ first_investments_df['地区'].isna())]
    first_investments_df['省份'] = first_investments_df['地区'].str.split('|').str[1]
    with pd.ExcelWriter('invest.xlsx', engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        first_investments_df.to_excel(writer, sheet_name='有专利公司首次投资', index=False)

def invest_filter_province():
    first_investments_df = pd.read_excel('invest.xlsx', sheet_name='有专利公司首次投资')
    first_investments_df.dropna(subset=['省份'],inplace=True)
    first_investments_df = first_investments_df[first_investments_df['省份'] != '台湾']
    with pd.ExcelWriter('invest.xlsx', engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        first_investments_df.to_excel(writer, sheet_name='有专利公司首次投资', index=False)

def rename_urban():
    file = '2000-2023年各省份城镇化水平.xlsx'
    urban_df = pd.read_excel(file, sheet_name='原始版本')
    urban_df.rename(columns={'省份': '地区'}, inplace=True)
    with pd.ExcelWriter(file, engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        urban_df.to_excel(writer, sheet_name='原始版本', index=False)

def add_ln():
    df = pd.read_excel('patent_analysis/regression_panel_data.xlsx', sheet_name='面板数据')
    df['lnGDP'] = np.log(df['GDP'] + 1)
    df['lnFixedInvestment'] = np.log(df['固定资产投资'] + 1)

    with pd.ExcelWriter('patent_analysis/regression_panel_data.xlsx', engine='openpyxl',mode='a',if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='面板数据1', index=False)

# def trim_tex(text)->str:
#     text = text.replace('二产就业比例','SIEP')
#     text = text.replace('城镇化率','UrbanizationRate')
#     tokens = text.split('\n')
#     index = list(range(0,20)) + list(range(60,66)) + [84] + list(range(86,94)) 
#     filtered_tokens = [tokens[i] for i in index]
#     filtered_tokens.insert(26,'省份固定效应  & 控制 & 控制 & 控制 & 控制 & 控制 \\\\ \n 年份固定效应  & 控制 & 控制 & 控制 & 控制 & 控制 \\\\ \n\hline\n')
#     return '\n'.join(filtered_tokens)+'\n\n'




def trim_stage_tex(text)->str:
    text = text.replace('二产就业比例','SIEP')
    text = text.replace('城镇化率','UrbanizationRate')
    tokens = text.split('\n')
    del tokens[21]
    tokens.insert(20,'省份固定效应  & 控制 & 控制 & 控制 & 控制  \\\\ \n 年份固定效应  & 控制 & 控制 & 控制 & 控制  \\\\ \n\hline\n')
    return '\n'.join(tokens)+'\n\n'

def trim_same_region_tex(text)->str:
    text = text.replace('二产就业比例','SIEP')
    text = text.replace('城镇化率','UrbanizationRate')
    tokens = text.split('\n') 
    del tokens[25]
    tokens.insert(24,'年份固定效应  & 控制 & 控制\\\\ \n\hline\n')
    return '\n'.join(tokens)+'\n\n'

def trim_region_tex(text)->str:
    text = text.replace('二产就业比例','SIEP')
    text = text.replace('城镇化率','UrbanizationRate')
    tokens = text.split('\n')
    del tokens[25]
    tokens.insert(24,'年份固定效应  & 控制 & 控制 & 控制 & 控制\\\\ \n\hline\n')
    return '\n'.join(tokens)+'\n\n'

def trim_gov_tex(text)->str:
    text = text.replace('二产就业比例','SIEP')
    text = text.replace('城镇化率','UrbanizationRate')
    tokens = text.split('\n')
    index = list(range(0,22)) + list(range(80,87))+list(range(88,len(tokens)))
    filtered_tokens = [tokens[i] for i in index]
    # filtered_tokens.insert(86,'省份固定效应  & 控制 & 控制 & 控制 & 控制  \\\\ \n 年份固定效应   & 控制 & 控制 & 控制 & 控制 \\\\ \n\hline\n')
    return '\n'.join(filtered_tokens)+'\n\n'


def stage_piechart():
    import matplotlib as mpl

# Set the font to a common Chinese font (e.g., HeiTi on macOS/Linux or SimHei on Windows)
# You may need to replace 'Heiti TC' with a font installed on your system.
    mpl.rcParams['font.sans-serif'] = ['Heiti TC', 'SimHei', 'Microsoft YaHei', 'Arial Unicode MS'] 
    # Also set up a font for supporting special characters and minus signs
    mpl.rcParams['axes.unicode_minus'] = False 
    size = [3036, 5610, 14904, 9576]
    labels = ['种子期','初创期','扩张期', '成熟期']
    plt.pie(size, labels=labels, autopct='%1.1f%%')
    plt.savefig('patent_analysis/graph/stage_piechart.png')

def read_fin_tight_industry():
    file = 'fin_tight_ind.csv'
    # 使用空格作为分隔符，第一行是数据不是列名
    df = pd.read_csv(file, delim_whitespace=True, header=None)
    
    # 将第二列的百分号数据转换为浮点数
    if len(df.columns) >= 2:
        # 使用列索引1访问第二列（因为header=None，列名是数字）
        col_idx = 1
        # 如果第二列是字符串类型且包含百分号，则转换
        if df[col_idx].dtype == 'object':
            # 去掉百分号并转换为浮点数
            df[col_idx] = df[col_idx].str.replace('%', '').astype(float) / 100
        elif df[col_idx].dtype in ['int64', 'float64']:
            # 如果已经是数值类型，假设是百分比形式（如50表示50%），转换为小数
            df[col_idx] = df[col_idx] / 100
    df.sort_values(by=1, ascending=True, inplace=True)
    return df
  
    

if __name__ == "__main__":
    # add_province_investment()
    # invest_filter_province()
    # add_ln()
    # trim_tex('6')
    # stage_piechart()
    read_fin_tight_industry()