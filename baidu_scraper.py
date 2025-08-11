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
        self.base_url = 'https://www.baidu.com/'
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
        
        # 忽略JavaScript debugger，避免渲染被暂停
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 禁用JavaScript调试功能
        chrome_options.add_argument("--disable-javascript-debugger")
        chrome_options.add_argument("--disable-breakpad")
        chrome_options.add_argument("--disable-crash-reporter")
        
        # 禁用开发者工具
        # chrome_options.add_argument("--disable-dev-tools")
        # chrome_options.add_argument("--disable-web-security")
        
        # # 禁用各种调试和监控功能
        # chrome_options.add_argument("--disable-logging")
        # chrome_options.add_argument("--disable-background-timer-throttling")
        # chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        # chrome_options.add_argument("--disable-renderer-backgrounding")

        # chrome_options.add_argument("--headless")  # 无头模式
        # chrome_options.add_argument("--disable-images")  # 禁用图片加载
        # chrome_options.add_argument("--disable-javascript")  # 禁用JavaScript（可选）
        # chrome_options.add_argument("--disable-plugins")  # 禁用插件
        # chrome_options.add_argument("--disable-extensions")  # 禁用扩展

        # 设置用户代理
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_cdp_cmd("Debugger.setBreakpointsActive", {"active": False})
            print("Chrome浏览器驱动初始化成功")
            return True
        except Exception as e:
            print(f"Chrome浏览器驱动初始化失败: {e}")
            return False
    
    def search_baidu(self, keyword):
        """在百度搜索指定关键词"""
        try:
            print(f"正在访问百度首页...")
            self.driver.get(self.base_url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 查找百度搜索输入框
            print("正在查找百度搜索输入框...")
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "chat-textarea"))
            )
            
            # 清空输入框并输入搜索关键词
            print(f"正在输入搜索关键词: {keyword}")
            search_input.clear()
            search_input.send_keys(keyword)
            
            # 查找百度搜索按钮并点击
            print("正在查找百度搜索按钮...")
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "chat-submit-button"))
            )
            
            print("点击搜索按钮...")
            search_button.click()
            
            # 等待搜索结果加载
            print("等待搜索结果加载...")
            time.sleep(3)
            
            # 获取搜索结果
            results = self.extract_baidu_results()
            
            return results
            
        except Exception as e:
            print(f"搜索过程中发生错误: {e}")
            return None
    
    def extract_baidu_results(self):
        """提取百度搜索结果"""
        try:
            print("正在提取百度搜索结果...")
            
            # 等待结果加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".result, .result-op, .c-container"))
            )
            
            # 获取搜索结果列表
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, ".result, .result-op, .c-container")
            
            results = []
            
            for i, element in enumerate(result_elements[:20]):  # 限制前20个结果
                try:
                    # 尝试提取搜索结果信息
                    result_info = self.extract_baidu_result_info(element)
                    if result_info:
                        results.append(result_info)
                except Exception as e:
                    print(f"提取第{i+1}个结果时出错: {e}")
                    continue
            
            print(f"成功提取 {len(results)} 个搜索结果")
            return results
            
        except Exception as e:
            print(f"提取搜索结果时发生错误: {e}")
            return []
    
    def extract_baidu_result_info(self, element):
        """从百度搜索结果元素中提取信息"""
        try:
            # 尝试提取标题
            title = ""
            title_selectors = ["h3", ".t", ".c-title", "a"]
            for selector in title_selectors:
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    if title:
                        break
                except:
                    continue
            
            # 尝试提取链接
            link = ""
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "a")
                link = link_elem.get_attribute("href")
            except:
                pass
            
            # 尝试提取摘要
            abstract = ""
            abstract_selectors = [".c-abstract", ".content", ".c-span-last", "p"]
            for selector in abstract_selectors:
                try:
                    abstract_elem = element.find_element(By.CSS_SELECTOR, selector)
                    abstract = abstract_elem.text.strip()
                    if abstract:
                        break
                except:
                    pass
            
            # 尝试提取来源信息
            source = ""
            try:
                source_elem = element.find_element(By.CSS_SELECTOR, ".c-author", ".c-color-gray")
                source = source_elem.text.strip()
            except:
                pass
            
            # 尝试提取时间信息
            time_info = ""
            try:
                time_elem = element.find_element(By.CSS_SELECTOR, ".c-color-gray2", ".c-color-gray")
                time_info = time_elem.text.strip()
            except:
                pass
            
            if title or abstract:
                return {
                    "title": title,
                    "link": link,
                    "abstract": abstract,
                    "source": source,
                    "time": time_info
                }
            
            return None
            
        except Exception as e:
            print(f"提取专利信息时出错: {e}")
            return None
    
    def save_results(self, results, filename="baidu_search_results.xlsx"):
        """保存百度搜索结果到Excel文件"""
        try:
            if results:
                df = pd.DataFrame(results)
                df.to_excel(filename, index=False)
                print(f"百度搜索结果已保存到 {filename}")
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
        
        # 搜索关键词
        keyword = "专利"
        print(f"开始在百度搜索: {keyword}")
        
        # 执行搜索
        results = scraper.search_baidu(keyword)
        
        if results:
            print(f"\n搜索完成，共找到 {len(results)} 个结果")
            
            # 显示前几个结果
            for i, result in enumerate(results[:5], 1):
                print(f"\n结果 {i}:")
                for key, value in result.items():
                    if value:  # 只显示非空值
                        print(f"  {key}: {value}")
            
            # 保存结果
            scraper.save_results(results, "baidu_search_results.xlsx")
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
