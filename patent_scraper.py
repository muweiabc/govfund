import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import json
import pandas as pd

class PatentScraper:
    def __init__(self):
        self.base_url = "https://pss-system.cponline.cnipa.gov.cn"
        self.driver = None
        
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        chrome_options = Options()
        # 设置无头模式（可选，注释掉可以看到浏览器操作过程）
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # 设置用户代理
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Chrome浏览器驱动初始化成功")
            return True
        except Exception as e:
            print(f"Chrome浏览器驱动初始化失败: {e}")
            return False
    
    def search_patent(self, company_name):
        """搜索指定公司的专利"""
        try:
            print(f"正在访问专利搜索系统...")
            self.driver.get(self.base_url)
            # try:
            #     element = WebDriverWait(driver, 10).until(
            #         EC.presence_of_element_located((By.ID, "my_element_id"))
            #     )
            #     # 此时，页面已加载，你可以开始获取内容
            #     print(element.text)
            # except:
            #     print("指定元素未在10秒内出现")
            # 等待页面加载
            time.sleep(5)
            
            # 查找搜索输入框
            print("正在查找搜索输入框...")
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], textarea, .search-input"))
            )
            
            # 清空输入框并输入搜索命令
            search_command = f"SS PA=({company_name})"
            print(f"正在输入搜索命令: {search_command}")
            search_input.clear()
            search_input.send_keys(search_command)
            
            # 查找搜索按钮并点击
            print("正在查找搜索按钮...")
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], .search-btn, .btn-search"))
            )
            
            print("点击搜索按钮...")
            search_button.click()
            
            # 等待搜索结果加载
            print("等待搜索结果加载...")
            time.sleep(5)
            
            # 获取搜索结果
            results = self.extract_search_results()
            
            return results
            
        except Exception as e:
            print(f"搜索过程中发生错误: {e}")
            return None
    
    def extract_search_results(self):
        """提取搜索结果"""
        try:
            print("正在提取搜索结果...")
            
            # 等待结果加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".result-item, .patent-item, .search-result"))
            )
            
            # 获取搜索结果列表
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, ".result-item, .patent-item, .search-result, tr")
            
            results = []
            
            for i, element in enumerate(result_elements[:20]):  # 限制前20个结果
                try:
                    # 尝试提取专利信息
                    patent_info = self.extract_patent_info(element)
                    if patent_info:
                        results.append(patent_info)
                except Exception as e:
                    print(f"提取第{i+1}个结果时出错: {e}")
                    continue
            
            print(f"成功提取 {len(results)} 个搜索结果")
            return results
            
        except Exception as e:
            print(f"提取搜索结果时发生错误: {e}")
            return []
    
    def extract_patent_info(self, element):
        """提取单个专利信息"""
        try:
            # 尝试不同的选择器来提取信息
            selectors = [
                ".patent-title, .title, h3, h4",
                ".patent-number, .number, .patent-no",
                ".applicant, .inventor, .author",
                ".abstract, .summary, .description"
            ]
            
            patent_info = {}
            
            for selector in selectors:
                try:
                    elements = element.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        patent_info[selector.replace('.', '').replace(',', '')] = elements[0].text.strip()
                except:
                    continue
            
            # 如果没有找到结构化信息，获取整个元素的文本
            if not patent_info:
                patent_info['raw_text'] = element.text.strip()
            
            return patent_info
            
        except Exception as e:
            print(f"提取专利信息时出错: {e}")
            return None
    
    def save_results(self, results, filename="patent_search_results.xlsx"):
        """保存搜索结果到Excel文件"""
        try:
            if results:
                df = pd.DataFrame(results)
                df.to_excel(filename, index=False)
                print(f"搜索结果已保存到 {filename}")
                return True
            else:
                print("没有搜索结果可保存")
                return False
        except Exception as e:
            print(f"保存结果时发生错误: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")

def main():
    """主函数"""
    scraper = PatentScraper()
    
    try:
        # 初始化浏览器驱动
        if not scraper.setup_driver():
            return
        
        # 搜索指定公司
        company_name = "航天智造科技股份有限公司"
        print(f"开始搜索公司: {company_name}")
        
        # 执行搜索
        results = scraper.search_patent(company_name)
        
        if results:
            print(f"\n搜索完成，共找到 {len(results)} 个结果")
            
            # 显示前几个结果
            for i, result in enumerate(results[:5], 1):
                print(f"\n结果 {i}:")
                for key, value in result.items():
                    print(f"  {key}: {value}")
            
            # 保存结果
            scraper.save_results(results)
        else:
            print("未找到搜索结果")
    
    except Exception as e:
        print(f"程序执行过程中发生错误: {e}")
    
    finally:
        # 等待用户查看结果后关闭
        input("\n按回车键关闭浏览器...")
        scraper.close()

if __name__ == "__main__":
    main()
