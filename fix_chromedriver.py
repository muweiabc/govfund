#!/usr/bin/env python3
"""
ChromeDriver修复脚本
专门用于解决Mac ARM64系统上的ChromeDriver问题
"""

import os
import platform
import subprocess
import sys

def check_system():
    """检查系统信息"""
    print(f"操作系统: {platform.system()}")
    print(f"架构: {platform.machine()}")
    print(f"Python版本: {sys.version}")
    
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        print("检测到Mac ARM64系统")
        return True
    else:
        print("非Mac ARM64系统")
        return False

def check_chrome():
    """检查Chrome浏览器"""
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run([path, "--version"], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"找到Chrome浏览器: {result.stdout.strip()}")
                    return True
            except:
                continue
    
    print("未找到Chrome浏览器，请先安装Chrome")
    return False

def check_chromedriver():
    """检查ChromeDriver"""
    chromedriver_paths = [
        "/opt/homebrew/bin/chromedriver",
        "/usr/local/bin/chromedriver",
        os.path.expanduser("~/chromedriver")
    ]
    
    for path in chromedriver_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run([path, "--version"], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"找到ChromeDriver: {result.stdout.strip()}")
                    return path
            except:
                continue
    
    print("未找到ChromeDriver")
    return None

def install_chromedriver():
    """安装ChromeDriver"""
    print("正在安装ChromeDriver...")
    
    try:
        # 使用Homebrew安装
        result = subprocess.run(["brew", "install", "--cask", "chromedriver"], 
                             capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("ChromeDriver安装成功")
            return True
        else:
            print(f"Homebrew安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"安装过程中出错: {e}")
        return False

def clean_cache():
    """清理ChromeDriver缓存"""
    cache_dirs = [
        os.path.expanduser("~/.wdm"),
        os.path.expanduser("~/.cache/selenium"),
        os.path.expanduser("~/Library/Caches/selenium")
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                import shutil
                shutil.rmtree(cache_dir)
                print(f"已清理缓存: {cache_dir}")
            except Exception as e:
                print(f"清理缓存失败 {cache_dir}: {e}")

def main():
    """主函数"""
    print("=== ChromeDriver修复工具 ===\n")
    
    # 检查系统
    is_mac_arm64 = check_system()
    print()
    
    # 检查Chrome
    if not check_chrome():
        print("请先安装Chrome浏览器")
        return
    print()
    
    # 清理缓存
    print("清理ChromeDriver缓存...")
    clean_cache()
    print()
    
    # 检查ChromeDriver
    chromedriver_path = check_chromedriver()
    
    if not chromedriver_path:
        if is_mac_arm64:
            print("正在为Mac ARM64系统安装ChromeDriver...")
            if install_chromedriver():
                chromedriver_path = check_chromedriver()
            else:
                print("自动安装失败，请手动安装")
                print("手动安装步骤:")
                print("1. 访问 https://chromedriver.chromium.org/")
                print("2. 下载Mac ARM64版本")
                print("3. 解压并移动到 /opt/homebrew/bin/")
                return
        else:
            print("请手动安装ChromeDriver")
            return
    
    print(f"\nChromeDriver路径: {chromedriver_path}")
    print("ChromeDriver配置完成！")
    
    # 测试ChromeDriver
    print("\n正在测试ChromeDriver...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式测试
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("ChromeDriver测试成功！")
        driver.quit()
        
    except Exception as e:
        print(f"ChromeDriver测试失败: {e}")
        print("请检查Chrome和ChromeDriver版本是否兼容")

if __name__ == "__main__":
    main()
