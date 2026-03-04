from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import json
import os
from datetime import datetime
import re

class NowCoderCrawler:
    def __init__(self, cookie_file='cookie.txt'):
        """初始化爬虫"""
        # 设置Chrome选项
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')  # 如需后台运行，取消注释
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # 初始化浏览器 - 使用 Selenium 自动管理驱动
        try:
            # 检查本地是否有 chromedriver.exe
            local_driver = os.path.join(os.getcwd(), 'chromedriver.exe')
            if os.path.exists(local_driver):
                print(f"✓ 使用本地 ChromeDriver: {local_driver}")
                service = Service(local_driver)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Selenium 4.6+ 会自动下载并管理驱动
                print("✓ 使用 Selenium 自动管理驱动")
                self.driver = webdriver.Chrome(options=chrome_options)
            print("✓ 浏览器启动成功")
        except Exception as e:
            print(f"✗ 浏览器启动失败: {e}")
            print("\n可能的解决方案:")
            print("1. 确保已安装 Chrome 浏览器")
            print("2. 升级 Selenium: pip install --upgrade selenium")
            print("3. 手动下载 ChromeDriver (win64版本) 并放到项目目录")
            print("   下载地址: https://googlechromelabs.github.io/chrome-for-testing/")
            raise
        
        self.wait = WebDriverWait(self.driver, 10)
        
        # 创建输出目录
        self.output_dir = 'output'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"✓ 创建输出目录: {self.output_dir}")
        
        # 读取cookie
        self.cookies = self.load_cookies(cookie_file)
        
    def load_cookies(self, cookie_file):
        """从文件读取cookie"""
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookie_str = f.read().strip()
        
        cookies = {}
        for item in cookie_str.split('; '):
            if '=' in item:
                key, value = item.split('=', 1)
                cookies[key] = value
        return cookies
    
    def set_cookies(self):
        """设置cookie到浏览器"""
        for name, value in self.cookies.items():
            self.driver.add_cookie({
                'name': name,
                'value': value,
                'domain': '.nowcoder.com'
            })
    
    def crawl_page(self, url):
        """爬取单个页面的所有题目"""
        print(f"\n{'='*80}")
        print(f"正在访问: {url}")
        print(f"{'='*80}")
        
        # 首先访问主域名以设置cookie
        print("\n步骤1: 访问主域名设置cookie...")
        self.driver.get("https://www.nowcoder.com")
        time.sleep(2)
        
        # 设置cookie
        print("步骤2: 设置cookie...")
        self.set_cookies()
        print(f"✓ 已设置 {len(self.cookies)} 个cookie")
        
        # 访问目标页面
        print(f"\n步骤3: 访问目标页面...")
        self.driver.get(url)
        time.sleep(5)  # 增加等待时间
        
        # 保存截图用于调试
        try:
            self.driver.save_screenshot('debug_page.png')
            print("✓ 页面截图已保存到 debug_page.png")
        except:
            pass
        
        # 打印页面标题
        print(f"页面标题: {self.driver.title}")
        
        # 等待问题列表加载 - 尝试多种选择器
        print("\n步骤4: 查找问题列表...")
        question_list = None
        selectors = [
            ".question-list",
            "[class*='question-list']",
            "div.interview-left-aside",
            ".el-scrollbar__wrap"
        ]
        
        for selector in selectors:
            try:
                print(f"尝试选择器: {selector}")
                question_list = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"✓ 找到问题列表容器: {selector}")
                break
            except Exception as e:
                print(f"✗ 未找到: {selector}")
                continue
        
        if not question_list:
            print("\n✗ 无法找到问题列表！")
            print("页面HTML（前1000字符）:")
            print(self.driver.page_source[:1000])
            return []
        
        # 获取所有问题元素 - 根据实际HTML结构使用ID选择器
        print("\n步骤5: 获取问题列表...")
        
        # 通过ID查找所有问题(interviewItem0, interviewItem1, ...)
        questions = []
        i = 0
        while True:
            try:
                question = self.driver.find_element(By.ID, f"interviewItem{i}")
                questions.append(question)
                i += 1
            except:
                break
        
        print(f"✓ 找到 {len(questions)} 个问题")
        
        if len(questions) == 0:
            print("\n✗ 未找到任何问题！")
            return []
        
        results = []
        
        # 遍历每个问题
        for i in range(len(questions)):
            try:
                # 通过ID重新获取问题元素
                question = self.driver.find_element(By.ID, f"interviewItem{i}")
                
                # 获取问题标题
                title = question.text.strip()
                if not title:
                    title = f"问题 {i+1}"
                
                print(f"\n{'='*60}")
                print(f"正在处理第 {i+1}/{len(questions)} 个问题: {title}")
                print(f"{'='*60}")
                
                # 滚动到元素位置
                self.driver.execute_script("arguments[0].scrollIntoView(true);", question)
                time.sleep(0.5)
                
                # 点击问题
                try:
                    question.click()
                except:
                    # 如果普通点击失败，使用JavaScript点击
                    self.driver.execute_script("arguments[0].click();", question)
                time.sleep(3)  # 增加等待时间
                
                # 提取问题内容
                content = self.extract_question_content()
                
                if content:
                    result_data = {
                        'index': i + 1,
                        'title': title,
                        'question': content['question'],
                        'answer': content['answer']
                    }
                    results.append(result_data)
                    print(f"✓ 成功提取内容")
                    
                    # 立即保存为Markdown文件
                    self.save_question_as_markdown(result_data, url)
                else:
                    print(f"✗ 提取内容失败")
                
                # 返回列表页（如果需要）
                # self.driver.back()
                # time.sleep(2)
                
            except Exception as e:
                print(f"处理问题 {i+1} 时出错: {e}")
                continue
        
        return results
    
    def extract_question_content(self):
        """提取单个问题的内容"""
        try:
            print("  → 等待页面加载...")
            time.sleep(2)
            
            # 保存当前页面截图
            try:
                self.driver.save_screenshot('debug_question.png')
                print("  → 问题页截图已保存到 debug_question.png")
            except:
                pass
            
            # 等待问题描述区域加载 - 尝试多种选择器
            question_desc_selectors = [".question-desc", "[class*='question-desc']", ".main-content"]
            question_element = None
            
            for selector in question_desc_selectors:
                try:
                    question_element = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"  → 找到问题描述区域: {selector}")
                    break
                except:
                    continue
            
            # 获取问题描述
            try:
                if question_element:
                    # 先尝试获取具体的问题内容区域
                    try:
                        question_content = question_element.find_element(By.CSS_SELECTOR, ".question-desc-content")
                        question_html = question_content.get_attribute('innerHTML')
                    except:
                        question_html = question_element.get_attribute('innerHTML')
                else:
                    question_html = "未找到问题描述"
                print(f"  → 问题描述长度: {len(question_html)} 字符")
            except:
                question_html = "未找到问题描述"
            
            # 查找并点击"查看解题思路"按钮
            print("  → 查找'查看解题思路'按钮...")
            try:
                # 根据实际HTML,按钮有特定的class
                button_selectors = [
                    "[class*='tw-bg-green-500']",
                    ".tw-bg-green-500",
                    "div[class*='tw-cursor-pointer'][class*='tw-bg-green']"
                ]
                
                button = None
                for selector in button_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            elem_text = elem.text
                            if elem_text and ('查看' in elem_text or '解题' in elem_text or '思路' in elem_text):
                                button = elem
                                print(f"  → 找到按钮: '{elem_text}'")
                                break
                        if button:
                            break
                    except Exception as e:
                        continue
                
                if button:
                    print("  → 正在点击按钮...")
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(1)
                    try:
                        button.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(3)
                    print("  ✓ 按钮点击成功，等待内容加载...")
                else:
                    print("  ✗ 未找到按钮")
                
            except Exception as e:
                print(f"  ✗ 点击按钮时出错: {e}")
            
            # 提取答案内容
            print("  → 提取答案内容...")
            try:
                # 等待内容显示
                time.sleep(2)
                
                # 查找答案区域 (根据HTML结构)
                answer_element = self.driver.find_element(By.CSS_SELECTOR, ".question-answer-wrap")
                
                # 尝试获取.answer-brief元素（实际答案内容）
                answer_html = ""
                try:
                    answer_brief = answer_element.find_element(By.CSS_SELECTOR, ".answer-brief")
                    answer_html = answer_brief.get_attribute('innerHTML')
                except:
                    # 如果没有.answer-brief，尝试获取整个区域
                    # 查找所有display不为none的div
                    answer_divs = answer_element.find_elements(By.CSS_SELECTOR, "div")
                    for div in answer_divs:
                        style = div.get_attribute("style") or ""
                        if "display:none" not in style and "display: none" not in style:
                            # 检查是否包含实际内容
                            if div.find_elements(By.TAG_NAME, "h2") or div.find_elements(By.TAG_NAME, "table"):
                                answer_html = div.get_attribute('innerHTML')
                                break
                
                if not answer_html:
                    # 最后尝试：获取整个答案区域
                    answer_html = answer_element.get_attribute('innerHTML')
                
                # 将HTML转换为Markdown
                answer_text = self.html_to_markdown(answer_html)
                
                print(f"  → 答案长度: {len(answer_text)} 字符")
                    
            except Exception as e:
                print(f"  ✗ 提取答案失败: {e}")
                answer_text = "未找到答案内容"
            
            # 处理问题描述
            question_text = self.html_to_markdown(question_html)
            
            result = {
                'question': question_text,
                'answer': answer_text
            }
            
            print(f"  ✓ 内容提取完成 - 问题:{len(question_text)}字 答案:{len(answer_text)}字")
            return result
            
        except Exception as e:
            print(f"提取内容时出错: {e}")
            return None
    
    def html_to_markdown(self, html_content):
        """将HTML内容转换为Markdown格式"""
        if not html_content:
            return ""
        
        # 解码HTML实体
        import html
        content = html.unescape(html_content)
        
        # 转换表格
        content = self.convert_table_to_markdown(content)
        
        # 转换标题 (h1-h4) - 清理多余空格
        content = re.sub(r'<h1[^>]*>(.*?)</h1>', lambda m: f"\n# {' '.join(re.sub(r'<[^>]+>', '', m.group(1)).split())}\n", content, flags=re.DOTALL)
        content = re.sub(r'<h2[^>]*>(.*?)</h2>', lambda m: f"\n## {' '.join(re.sub(r'<[^>]+>', '', m.group(1)).split())}\n", content, flags=re.DOTALL)
        content = re.sub(r'<h3[^>]*>(.*?)</h3>', lambda m: f"\n### {' '.join(re.sub(r'<[^>]+>', '', m.group(1)).split())}\n", content, flags=re.DOTALL)
        content = re.sub(r'<h4[^>]*>(.*?)</h4>', lambda m: f"\n#### {' '.join(re.sub(r'<[^>]+>', '', m.group(1)).split())}\n", content, flags=re.DOTALL)
        
        # 转换代码块
        content = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', r'\n```\n\1\n```\n', content, flags=re.DOTALL)
        content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', content, flags=re.DOTALL)
        
        # 转换列表 - 使用数字列表并清理空格
        content = re.sub(r'<ul[^>]*>', r'\n', content)
        content = re.sub(r'</ul>', r'\n', content)
        content = re.sub(r'<ol[^>]*>', r'\n', content)
        content = re.sub(r'</ol>', r'\n', content)
        
        # 处理列表项 - 清理多余空格，使用数字编号
        li_items = re.findall(r'<li[^>]*>(.*?)</li>', content, flags=re.DOTALL)
        for i, item in enumerate(li_items, 1):
            clean_item = re.sub(r'<[^>]+>', '', item)  # 移除HTML标签
            clean_item = ' '.join(clean_item.split())  # 清理空格
            content = content.replace(f'<li{content[content.find("<li"):content.find(">", content.find("<li"))+1-3]}>{item}</li>', f'{i}. {clean_item}\n', 1)
        
        # 清理剩余的li标签
        content = re.sub(r'<li[^>]*>(.*?)</li>', lambda m: f"- {' '.join(re.sub(r'<[^>]+>', '', m.group(1)).split())}\n", content, flags=re.DOTALL)
        
        # 转换加粗和斜体
        content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL)
        content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', content, flags=re.DOTALL)
        content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content, flags=re.DOTALL)
        content = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', content, flags=re.DOTALL)
        
        # 转换链接（但排除"复制代码"链接）
        content = re.sub(r'<a[^>]*href=["\']#["\'][^>]*>复制代码</a>', '', content)  # 先移除复制代码链接
        content = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.DOTALL)
        
        # 转换图片 - 保留所有图片
        content = re.sub(r'<img[^>]*src=["\']([^"\']*)["\'][^>]*alt=["\']([^"\']*)["\'][^>]*>', r'![\2](\1)', content)
        content = re.sub(r'<img[^>]*src=["\']([^"\']*)["\'][^>]*>', r'![](\1)', content)
        
        # 转换段落和换行
        content = re.sub(r'<br\s*/?>', r'\n', content)
        content = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\1\n', content, flags=re.DOTALL)
        content = re.sub(r'<div[^>]*>(.*?)</div>', r'\1\n', content, flags=re.DOTALL)
        
        # 移除其他HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 移除各种形式的"复制代码"文本
        content = re.sub(r'\[?复制代码\]?\s*\(#\)', '', content)  # [复制代码](#)
        content = re.sub(r'^\s*复制代码\s*$', '', content, flags=re.MULTILINE)  # 单独一行的"复制代码"
        content = re.sub(r'复制代码\s*\n', '\n', content)  # 后面紧跟换行的"复制代码"
        
        # 清理每行的多余空格
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # 保留代码块和表格的格式
            if '```' in line or line.strip().startswith('|'):
                cleaned_lines.append(line)
            else:
                # 清理行内多余空格
                cleaned_line = ' '.join(line.split())
                cleaned_lines.append(cleaned_line)
        content = '\n'.join(cleaned_lines)
        
        # 清理多余的空行
        content = re.sub(r'\n{3,}', r'\n\n', content)
        
        return content.strip()
    
    def convert_table_to_markdown(self, html_content):
        """将HTML表格转换为Markdown表格格式"""
        import re
        
        def table_replacer(match):
            table_html = match.group(0)
            
            # 检查是否为代码表格(带有gutter和code类名的行号表格)
            if 'class="gutter"' in table_html or 'class="code"' in table_html:
                # 提取代码内容(跳过行号列)
                code_lines = []
                # 查找所有代码行
                code_divs = re.findall(r'<div[^>]*class="[^"]*line[^"]*"[^>]*>(.*?)</div>', table_html, flags=re.DOTALL)
                
                for line in code_divs:
                    # 跳过行号div
                    if re.search(r'class="[^"]*number\d+[^"]*"', line) and not '<code' in line:
                        continue
                    # 提取代码内容
                    code_text = re.sub(r'<code[^>]*class="[^"]*"[^>]*>', '', line)
                    code_text = re.sub(r'</code>', '', code_text)
                    code_text = re.sub(r'<[^>]+>', '', code_text)
                    # 解码HTML实体
                    code_text = code_text.replace('&nbsp;', ' ')
                    code_text = code_text.replace('&lt;', '<')
                    code_text = code_text.replace('&gt;', '>')
                    code_text = code_text.replace('&amp;', '&')
                    code_text = code_text.replace('&quot;', '"')
                    
                    if code_text.strip():
                        code_lines.append(code_text)
                
                if code_lines:
                    # 移除每行开头的独立数字行号
                    cleaned_lines = []
                    for line in code_lines:
                        # 移除行首的纯数字行号（可能带空格）
                        line = re.sub(r'^\s*\d+\s*$', '', line)
                        # 移除行首的"数字+空格+代码"格式中的数字部分
                        line = re.sub(r'^\s*\d+\s+', '', line)
                        if line.strip():  # 只保留非空行
                            cleaned_lines.append(line)
                    
                    return '\n\n```java\n' + '\n'.join(cleaned_lines) + '\n```\n\n'
            
            # 正常表格处理
            # 提取表头
            headers = re.findall(r'<th[^>]*>(.*?)</th>', table_html, flags=re.DOTALL)
            if not headers:
                # 如果没有th标签，尝试使用第一行的td
                first_row = re.search(r'<tr[^>]*>(.*?)</tr>', table_html, flags=re.DOTALL)
                if first_row:
                    headers = re.findall(r'<td[^>]*>(.*?)</td>', first_row.group(1), flags=re.DOTALL)
            
            # 清理表头HTML标签
            headers = [re.sub(r'<[^>]+>', '', h).strip() for h in headers]
            
            # 提取所有行
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, flags=re.DOTALL)
            
            markdown_table = []
            
            # 添加表头
            if headers:
                markdown_table.append('| ' + ' | '.join(headers) + ' |')
                markdown_table.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
            
            # 添加数据行
            for row in rows:
                # 跳过表头行
                if '<th' in row:
                    continue
                    
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, flags=re.DOTALL)
                # 清理单元格HTML标签
                cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                
                if cells and len(cells) == len(headers):
                    markdown_table.append('| ' + ' | '.join(cells) + ' |')
            
            return '\n' + '\n'.join(markdown_table) + '\n'
        
        # 替换所有表格
        result = re.sub(r'<table[^>]*>.*?</table>', table_replacer, html_content, flags=re.DOTALL)
        return result
    
    def save_question_as_markdown(self, question_data, source_url):
        """保存单个问题为Markdown文件"""
        try:
            # 生成文件名（使用题号和部分标题）
            index = question_data['index']
            title = question_data['title']
            # 清理标题中的非法字符
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '（', '）', '。', '，')).strip()
            safe_title = safe_title[:50]  # 限制长度
            
            filename = f"{index:02d}_{safe_title}.md"
            filepath = os.path.join(self.output_dir, filename)
            
            # 写入Markdown内容
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {question_data['title']}\n\n")
                f.write(f"**题号**: {question_data['index']}\n\n")
                f.write(f"**来源**: {source_url}\n\n")
                f.write(f"**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                f.write("## 题目\n\n")
                f.write(f"{question_data['question']}\n\n")
                f.write("---\n\n")
                f.write("## 解题思路\n\n")
                f.write(f"{question_data['answer']}\n")
            
            print(f"  ✓ 已保存到: {filepath}")
            
        except Exception as e:
            print(f"  ✗ 保存Markdown失败: {e}")
    
    def save_results(self, results, filename='results.json'):
        """保存结果到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到 {filename}")
    
    def close(self):
        """关闭浏览器"""
        self.driver.quit()


def main():
    # 目标URL列表
    urls = [
        "https://www.nowcoder.com/exam/interview/94883707/test?paperId=61536918&input=java&order=0",
        # 可以添加更多URL
    ]
    
    crawler = NowCoderCrawler(cookie_file='cookie.txt')
    
    try:
        all_results = []
        
        for url in urls:
            results = crawler.crawl_page(url)
            all_results.extend(results)
            print(f"\n从 {url} 爬取了 {len(results)} 个问题")
        
        # 保存结果
        crawler.save_results(all_results, 'nowcoder_questions.json')
        
        # 同时保存为更易读的文本格式
        with open('nowcoder_questions.txt', 'w', encoding='utf-8') as f:
            for item in all_results:
                f.write(f"\n{'='*80}\n")
                f.write(f"问题 {item['index']}: {item['title']}\n")
                f.write(f"{'='*80}\n\n")
                f.write(f"【问题描述】\n{item['question']}\n\n")
                f.write(f"【解题思路】\n{item['answer']}\n\n")
        
        # 生成Markdown索引文件
        index_file = os.path.join(crawler.output_dir, 'README.md')
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("# 牛客网面试题库\n\n")
            f.write(f"**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**题目总数**: {len(all_results)}\n\n")
            f.write("---\n\n")
            f.write("## 题目列表\n\n")
            for item in all_results:
                safe_title = "".join(c for c in item['title'] if c.isalnum() or c in (' ', '-', '_', '（', '）', '。', '，')).strip()[:50]
                filename = f"{item['index']:02d}_{safe_title}.md"
                f.write(f"{item['index']}. [{item['title']}]({filename})\n")
        
        print(f"\n✓ 爬取完成！共爬取 {len(all_results)} 个问题")
        print("结果已保存到:")
        print("  - nowcoder_questions.json (JSON格式)")
        print("  - nowcoder_questions.txt (文本格式)")
        print(f"  - {crawler.output_dir}/README.md (Markdown索引)")
        print(f"  - {crawler.output_dir}/ (各题目的Markdown文件)")
        
    except Exception as e:
        print(f"爬取过程出错: {e}")
    finally:
        crawler.close()


if __name__ == "__main__":
    main()
