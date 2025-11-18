import pandas as pd

def check_industry(filename='govfund_filtered.xlsx'):
    df = pd.read_excel('invest.xlsx', sheet_name='有专利公司首次投资')
    def splitind(str):
        return str.split('|')[0]

    ind = df['行业(国标)'].apply(splitind)
    print(ind.value_counts())
if __name__ == "__main__":
   
    check_industry()