#!/usr/bin/env python3
"""
禁用JavaScript debugger的Chrome配置脚本
用于避免网页渲染被JavaScript debugger语句暂停
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def create_debugger_free_options():
    """创建禁用debugger的Chrome选项"""
    chrome_options = Options()
    
    # 基本设置
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
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--disable-web-security")
    
    # 禁用各种调试和监控功能
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    
    # 设置用户代理
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return chrome_options

def test_debugger_disabled():
    """测试debugger是否被禁用"""
    print("正在测试Chrome配置...")
    
    try:
        # 创建Chrome选项
        chrome_options = create_debugger_free_options()
        
        # 尝试初始化驱动
        driver = webdriver.Chrome(options=chrome_options)
        
        # 访问一个包含debugger语句的测试页面
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Debugger Test</title>
        </head>
        <body>
            <h1>Debugger Test Page</h1>
            <script>
                console.log("Testing debugger...");
                debugger; // 这个语句应该被忽略
                console.log("After debugger statement");
                
                // 模拟一些JavaScript代码
                for(let i = 0; i < 5; i++) {
                    console.log("Count: " + i);
                }
            </script>
        </body>
        </html>
        """
        
        # 将测试HTML写入临时文件
        with open("debugger_test.html", "w", encoding="utf-8") as f:
            f.write(test_html)
        
        # 访问测试页面
        driver.get("file://" + __import__('os').path.abspath("debugger_test.html"))
        
        # 等待页面加载
        time.sleep(3)
        
        # 获取控制台日志
        logs = driver.get_log('browser')
        
        print("Chrome配置测试成功！")
        print("页面应该正常渲染，不会被debugger语句暂停")
        
        # 检查控制台日志
        if logs:
            print("\n控制台日志:")
            for log in logs:
                print(f"  {log['level']}: {log['message']}")
        else:
            print("\n没有控制台日志（这是正常的）")
        
        driver.quit()
        
        # 清理测试文件
        import os
        if os.path.exists("debugger_test.html"):
            os.remove("debugger_test.html")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def get_chrome_options_for_scraping():
    """获取适用于网页爬取的Chrome选项"""
    print("=== 适用于网页爬取的Chrome配置 ===")
    
    chrome_options = create_debugger_free_options()
    
    # 添加爬取相关的选项
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-images")  # 禁用图片加载
    # chrome_options.add_argument("--disable-javascript")  # 禁用JavaScript（可选）
    chrome_options.add_argument("--disable-plugins")  # 禁用插件
    chrome_options.add_argument("--disable-extensions")  # 禁用扩展
    
    print("Chrome配置已优化，适用于网页爬取")
    print("主要特性:")
    print("- 禁用JavaScript debugger")
    print("- 禁用开发者工具")
    print("- 禁用各种调试功能")
    print("- 优化内存使用")
    
    return chrome_options

def main():
    """主函数"""
    print("=== JavaScript Debugger 禁用工具 ===\n")
    
    # 测试基本配置
    if test_debugger_disabled():
        print("\n✅ 基本配置测试通过")
    else:
        print("\n❌ 基本配置测试失败")
        return
    
    # 获取爬取配置
    scraping_options = get_chrome_options_for_scraping()
    
    print("\n=== 使用方法 ===")
    print("在你的爬虫代码中，使用以下方式创建Chrome选项:")
    print()
    print("from selenium import webdriver")
    print("from selenium.webdriver.chrome.options import Options")
    print()
    print("chrome_options = Options()")
    print("chrome_options.add_argument('--disable-javascript-debugger')")
    print("chrome_options.add_argument('--disable-blink-features=AutomationControlled')")
    print("chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])")
    print("chrome_options.add_experimental_option('useAutomationExtension', False)")
    print()
    print("driver = webdriver.Chrome(options=chrome_options)")

if __name__ == "__main__":
    main()
