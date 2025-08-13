from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from selenium.webdriver.common.keys import Keys

def setup_driver():
    """自动设置Chrome浏览器驱动"""
    try:
        chrome_options = Options()
        # 设置无头模式（可选）
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
        
        # 针对Mac ARM64的特殊处理
        import platform
        import os
        
        # 清理可能损坏的ChromeDriver缓存
        cache_dir = os.path.expanduser("~/.wdm")
        if os.path.exists(cache_dir):
            import shutil
            try:
                shutil.rmtree(cache_dir)
                print("已清理ChromeDriver缓存")
            except Exception as e:
                print(f"清理缓存时出错: {e}")
        
        # 自动下载并设置Chrome驱动
        try:
            # 尝试使用ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"ChromeDriverManager失败: {e}")
            # 尝试手动指定ChromeDriver路径
            if platform.system() == "Darwin" and platform.machine() == "arm64":
                # Mac ARM64
                chromedriver_path = "/opt/homebrew/bin/chromedriver"
                if os.path.exists(chromedriver_path):
                    service = Service(chromedriver_path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    # 尝试安装ChromeDriver
                    print("正在安装ChromeDriver...")
                    os.system("brew install --cask chromedriver")
                    if os.path.exists(chromedriver_path):
                        service = Service(chromedriver_path)
                        driver = webdriver.Chrome(service=service, options=chrome_options)
                    else:
                        raise Exception("无法找到或安装ChromeDriver")
            else:
                raise e
        
        print("Chrome浏览器驱动初始化成功")
        return driver
        
    except Exception as e:
        print(f"Chrome浏览器驱动初始化失败: {e}")
        print("请尝试以下解决方案:")
        print("1. 运行: brew install --cask chromedriver")
        print("2. 或者访问 https://chromedriver.chromium.org/ 手动下载对应版本")
        print("3. 确保Chrome浏览器已安装且版本与ChromeDriver兼容")
        return None

def search_patents(company_name):
    """搜索指定公司的专利"""
    driver = None
    
    try:
        # 初始化驱动
        driver = setup_driver()
        if not driver:
            return None
        
        # 访问专利搜索系统
        url = "https://pss-system.cponline.cnipa.gov.cn/commandSearch"
        print(f"正在访问: {url}")
        driver.get(url)
        
        # 等待页面加载
        time.sleep(5)
        
        # 查找搜索输入框（尝试多种选择器）
        search_input = None
        selectors = [
            "input[type='text']",
            "textarea",
            ".search-input",
            "#searchInput",
            "[placeholder*='搜索']",
            "[placeholder*='输入']"
        ]
        
        for selector in selectors:
            try:
                search_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"找到搜索输入框，使用选择器: {selector}")
                break
            except:
                continue
        
        if not search_input:
            print("未找到搜索输入框")
            # 保存页面源码以便调试
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("页面源码已保存到 page_source.html")
            return None
        
        # 输入搜索命令
        search_command = f"SS PA=({company_name})"
        print(f"正在输入搜索命令: {search_command}")
        search_input.clear()
        search_input.send_keys(search_command)
        
        # 查找搜索按钮
        search_button = None
        button_selectors = [
            "button[type='submit']",
            ".search-btn",
            ".btn-search",
            "button:contains('搜索')",
            "input[type='submit']"
        ]
        
        for selector in button_selectors:
            try:
                search_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                print(f"找到搜索按钮，使用选择器: {selector}")
                break
            except:
                continue
        
        if not search_button:
            # 尝试按回车键
            print("未找到搜索按钮，尝试按回车键")
            search_input.send_keys(Keys.RETURN)
        else:
            print("点击搜索按钮")
            search_button.click()
        
        # 等待搜索结果
        print("等待搜索结果加载...")
        time.sleep(8)
        
        # 提取搜索结果
        results = extract_results(driver)
        
        return results
        
    except Exception as e:
        print(f"搜索过程中发生错误: {e}")
        return None
    
    finally:
        if driver:
            driver.quit()
            print("浏览器已关闭")

def extract_results(driver):
    """提取搜索结果"""
    try:
        print("正在提取搜索结果...")
        
        # 尝试多种结果选择器
        result_selectors = [
            ".result-item",
            ".patent-item", 
            ".search-result",
            "tr",
            ".list-item",
            ".item"
        ]
        
        results = []
        
        for selector in result_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 1:  # 排除表头等
                    print(f"使用选择器 {selector} 找到 {len(elements)} 个元素")
                    
                    for i, element in enumerate(elements[:20]):  # 限制前20个
                        try:
                            text = element.text.strip()
                            if text and len(text) > 10:  # 过滤掉太短的文本
                                results.append({
                                    '序号': i + 1,
                                    '内容': text,
                                    '选择器': selector
                                })
                        except:
                            continue
                    
                    if results:
                        break
                        
            except Exception as e:
                print(f"使用选择器 {selector} 时出错: {e}")
                continue
        
        if not results:
            # 如果没找到结果，保存页面源码
            print("未找到搜索结果，保存页面源码...")
            with open("search_results_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("搜索结果页面源码已保存到 search_results_page.html")
        
        return results
        
    except Exception as e:
        print(f"提取结果时发生错误: {e}")
        return []

def main():
    """主函数"""
    company_name = "航天智造科技股份有限公司"
    print(f"开始搜索公司专利: {company_name}")
    
    # 执行搜索
    results = search_patents(company_name)
    
    if results:
        print(f"\n搜索完成，共找到 {len(results)} 个结果")
        
        # 显示结果
        for result in results[:10]:  # 显示前10个
            print(f"\n{result['序号']}. {result['内容'][:100]}...")
        
        # 保存结果
        df = pd.DataFrame(results)
        filename = f"patent_search_{company_name}.xlsx"
        df.to_excel(filename, index=False)
        print(f"\n搜索结果已保存到 {filename}")
        
    else:
        print("未找到搜索结果")

if __name__ == "__main__":
    main()
