import pandas as pd
path = '../'
files = ['patent2025','中国专利数据库2024年']
patent_df = pd.read_csv(path + files[1]+'.csv')
sdf = patent_df.loc[:,['专利类型','申请人','申请年份','公开公告年份']]
sdf.to_csv((files[1]+'trim.csv'),index=False)
                 
