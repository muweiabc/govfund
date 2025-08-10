# ChromeDriver 问题解决方案

## 问题描述
在Mac ARM64系统上运行专利爬虫时遇到ChromeDriver初始化失败的错误：
```
Chrome浏览器驱动初始化失败: [Errno 8] Exec format error: '/Users/muwei/.wdm/drivers/chromedriver/mac64/138.0.7204.183/chromedriver-mac-arm64/THIRD_PARTY_NOTICES.chromedriver'
```

## 问题原因
1. **架构不匹配**: 系统是Mac ARM64，但下载的ChromeDriver可能是Intel版本
2. **缓存损坏**: webdriver-manager的缓存文件损坏
3. **版本不兼容**: ChromeDriver版本与Chrome浏览器版本不匹配

## 解决方案

### 方案1: 使用修复脚本（推荐）
运行我创建的修复脚本：
```bash
python fix_chromedriver.py
```

这个脚本会：
- 检查系统信息
- 清理损坏的缓存
- 自动安装正确的ChromeDriver
- 测试ChromeDriver是否工作

### 方案2: 手动安装ChromeDriver

#### 步骤1: 清理缓存
```bash
rm -rf ~/.wdm
rm -rf ~/.cache/selenium
rm -rf ~/Library/Caches/selenium
```

#### 步骤2: 使用Homebrew安装
```bash
brew install --cask chromedriver
```

#### 步骤3: 验证安装
```bash
chromedriver --version
```

### 方案3: 手动下载安装

#### 步骤1: 检查Chrome版本
1. 打开Chrome浏览器
2. 在地址栏输入: `chrome://version/`
3. 记下版本号（如：138.0.7204.183）

#### 步骤2: 下载对应版本的ChromeDriver
1. 访问: https://chromedriver.chromium.org/
2. 下载与Chrome版本匹配的Mac ARM64版本
3. 解压下载的文件

#### 步骤3: 安装ChromeDriver
```bash
# 移动到系统路径
sudo mv chromedriver /opt/homebrew/bin/

# 设置执行权限
sudo chmod +x /opt/homebrew/bin/chromedriver

# 验证安装
chromedriver --version
```

## 代码修改说明

我已经修改了 `patent_scraper_simple.py` 文件，主要改进包括：

1. **自动清理缓存**: 在初始化前清理可能损坏的ChromeDriver缓存
2. **架构检测**: 自动检测Mac ARM64系统
3. **备用方案**: 如果ChromeDriverManager失败，尝试使用系统安装的ChromeDriver
4. **自动安装**: 尝试使用Homebrew自动安装ChromeDriver
5. **详细错误信息**: 提供具体的解决步骤

## 常见问题

### Q: 仍然出现权限错误怎么办？
A: 运行以下命令：
```bash
sudo xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```

### Q: ChromeDriver版本不匹配怎么办？
A: 确保ChromeDriver版本与Chrome浏览器版本完全匹配

### Q: 可以同时运行多个Chrome实例吗？
A: 可以，但建议添加不同的用户数据目录：
```python
chrome_options.add_argument("--user-data-dir=/tmp/chrome_profile_1")
```

## 测试验证

运行修复脚本后，可以测试ChromeDriver是否正常工作：

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")

service = Service("/opt/homebrew/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

print("ChromeDriver工作正常！")
driver.quit()
```

## 联系支持

如果问题仍然存在，请：
1. 运行 `python fix_chromedriver.py` 并查看完整输出
2. 检查Chrome浏览器版本
3. 提供完整的错误信息
