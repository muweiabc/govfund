import pandas as pd

def find_duplicate_rows(filename='govfund_filtered.xlsx'):
    """
    查找govfund_filtered文件里重复的行
    """
    try:
        # 读取文件
        print(f"正在读取 {filename}...")
        df = pd.read_excel(filename)
        
        print(f"数据总行数: {len(df)}")
        print(f"数据总列数: {len(df.columns)}")
        
        # 查找完全重复的行
        duplicated_rows = df[df.duplicated()]
        print(f"\n完全重复的行数: {len(duplicated_rows)}")
        
        if len(duplicated_rows) > 0:
            print("\n完全重复的行:")
            print(duplicated_rows)
            
            # 保存重复行到新文件
            duplicated_rows.to_excel('duplicate_rows.xlsx', index=False)
            print(f"\n重复行已保存到 duplicate_rows.xlsx")
        
        # 基于关键列查找重复（基金简称）
        if '基金简称' in df.columns:
            fund_duplicates = df[df.duplicated(subset=['基金简称'], keep=False)]
            print(f"\n基于'基金简称'的重复行数: {len(fund_duplicates)}")
            
            if len(fund_duplicates) > 0:
                print("\n基于'基金简称'的重复行:")
                # 按基金简称排序以便查看
                fund_duplicates_sorted = fund_duplicates.sort_values('基金简称')
                print(fund_duplicates_sorted[['基金简称', '基金全称', '管理机构', '数据来源']])
                
                # 保存基金简称重复行到新文件
                fund_duplicates_sorted.to_excel('fund_name_duplicates.xlsx', index=False)
                print(f"\n基金简称重复行已保存到 fund_name_duplicates.xlsx")
                
                # 统计每个基金简称的重复次数
                duplicate_counts = fund_duplicates['基金简称'].value_counts()
                print(f"\n重复次数统计:")
                print(duplicate_counts.head(10))
        
        # 基于关键列组合查找重复（基金简称 + 管理机构）
        if '基金简称' in df.columns and '管理机构' in df.columns:
            combo_duplicates = df[df.duplicated(subset=['基金简称', '管理机构'], keep=False)]
            print(f"\n基于'基金简称+管理机构'的重复行数: {len(combo_duplicates)}")
            
            if len(combo_duplicates) > 0:
                combo_duplicates_sorted = combo_duplicates.sort_values(['基金简称', '管理机构'])
                combo_duplicates_sorted.to_excel('combo_duplicates.xlsx', index=False)
                print(f"基金简称+管理机构重复行已保存到 combo_duplicates.xlsx")
        
        # 返回去重后的数据统计
        df_deduplicated = df.drop_duplicates()
        print(f"\n去重后行数: {len(df_deduplicated)}")
        print(f"删除的重复行数: {len(df) - len(df_deduplicated)}")
        
        return {
            'total_rows': len(df),
            'duplicate_rows': len(duplicated_rows),
            'fund_name_duplicates': len(fund_duplicates) if '基金简称' in df.columns else 0,
            'combo_duplicates': len(combo_duplicates) if '基金简称' in df.columns and '管理机构' in df.columns else 0,
            'deduplicated_rows': len(df_deduplicated)
        }
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {filename}")
        return None
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
        return None

def remove_duplicates(filename='govfund_filtered.xlsx', output_filename='govfund_deduplicated.xlsx'):
    """
    去除重复行并保存到新文件
    """
    try:
        print(f"正在去重 {filename}...")
        df = pd.read_excel(filename)
        
        # 去除完全重复的行
        df_deduplicated = df.drop_duplicates()
        
        # 保存去重后的数据
        df_deduplicated.to_excel(output_filename, index=False)
        
        print(f"原始行数: {len(df)}")
        print(f"去重后行数: {len(df_deduplicated)}")
        print(f"删除的重复行数: {len(df) - len(df_deduplicated)}")
        print(f"去重后的数据已保存到 {output_filename}")
        
        return df_deduplicated
        
    except Exception as e:
        print(f"去重过程中发生错误: {e}")
        return None

if __name__ == "__main__":
    # 查找重复行
    result = find_duplicate_rows()
    
    if result:
        print(f"\n=== 重复行统计 ===")
        print(f"总行数: {result['total_rows']}")
        print(f"完全重复行数: {result['duplicate_rows']}")
        print(f"基金简称重复行数: {result['fund_name_duplicates']}")
        print(f"基金简称+管理机构重复行数: {result['combo_duplicates']}")
        print(f"去重后行数: {result['deduplicated_rows']}")
        
        # 如果有重复行，询问是否要去重
        if result['duplicate_rows'].shape[0] > 0:
            print(f"\n检测到 {result['duplicate_rows']} 行完全重复的数据")
            # 自动执行去重
            remove_duplicates()
