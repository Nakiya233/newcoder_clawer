"""
牛客网爬虫主模块
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import os

from config import (
    CHROME_OPTIONS, WAIT_TIMEOUT, PAGE_LOAD_WAIT, BUTTON_CLICK_WAIT,
    SCROLL_WAIT, OUTPUT_DIR, QUESTION_LIST_SELECTORS, QUESTION_DESC_SELECTORS,
    BUTTON_SELECTORS, BUTTON_KEYWORDS, BASE_URL, COOKIE_DOMAIN
)
from utils import load_cookies, ensure_directory
from html_converter import HTMLToMarkdownConverter
from file_handler import FileHandler


class NowCoderCrawler:
    """牛客网面试题爬虫"""
    
    def __init__(self, cookie_file):
        """
        初始化爬虫
        
        Args:
            cookie_file: cookie文件路径
        """
        self.driver = self._init_browser()
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)
        self.converter = HTMLToMarkdownConverter()
        
        # 创建输出目录
        ensure_directory(OUTPUT_DIR)
        self.file_handler = FileHandler(OUTPUT_DIR)
        
        # 读取cookie
        self.cookies = load_cookies(cookie_file)
    
    def _init_browser(self):
        """初始化浏览器"""
        chrome_options = webdriver.ChromeOptions()
        for option in CHROME_OPTIONS:
            chrome_options.add_argument(option)
        
        try:
            # 检查本地ChromeDriver
            local_driver = os.path.join(os.getcwd(), 'chromedriver.exe')
            if os.path.exists(local_driver):
                print(f"✓ 使用本地 ChromeDriver: {local_driver}")
                service = Service(local_driver)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                print("✓ 使用 Selenium 自动管理驱动")
                driver = webdriver.Chrome(options=chrome_options)
            
            print("✓ 浏览器启动成功")
            return driver
            
        except Exception as e:
            print(f"✗ 浏览器启动失败: {e}")
            print("\n可能的解决方案:")
            print("1. 确保已安装 Chrome 浏览器")
            print("2. 升级 Selenium: pip install --upgrade selenium")
            print("3. 手动下载 ChromeDriver (win64版本) 并放到项目目录")
            raise
    
    def _set_cookies(self):
        """设置cookie到浏览器"""
        for name, value in self.cookies.items():
            self.driver.add_cookie({
                'name': name,
                'value': value,
                'domain': COOKIE_DOMAIN
            })
    
    def crawl_page(self, url):
        """
        爬取单个页面的所有题目
        
        Args:
            url: 目标页面URL
            
        Returns:
            list: 爬取结果列表
        """
        print(f"\n{'='*80}")
        print(f"正在访问: {url}")
        print(f"{'='*80}")
        
        # 访问主域名设置cookie
        print("\n步骤1: 访问主域名设置cookie...")
        self.driver.get(BASE_URL)
        time.sleep(2)
        
        print("步骤2: 设置cookie...")
        self._set_cookies()
        print(f"✓ 已设置 {len(self.cookies)} 个cookie")
        
        # 访问目标页面
        print(f"\n步骤3: 访问目标页面...")
        self.driver.get(url)
        time.sleep(PAGE_LOAD_WAIT)
        print(f"页面标题: {self.driver.title}")
        
        # 查找问题列表
        print("\n步骤4: 查找问题列表...")
        if not self._find_question_list():
            return []
        
        # 获取所有问题
        print("\n步骤5: 获取问题列表...")
        questions = self._get_all_questions()
        print(f"✓ 找到 {len(questions)} 个问题")
        
        if len(questions) == 0:
            print("\n✗ 未找到任何问题！")
            return []
        
        # 处理每个问题
        results = self._process_questions(questions, url)
        return results
    
    def _find_question_list(self):
        """查找问题列表容器"""
        for selector in QUESTION_LIST_SELECTORS:
            try:
                print(f"尝试选择器: {selector}")
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"✓ 找到问题列表容器: {selector}")
                return True
            except:
                print(f"✗ 未找到: {selector}")
                continue
        
        print("\n✗ 无法找到问题列表！")
        return False
    
    def _get_all_questions(self):
        """获取所有问题元素"""
        questions = []
        i = 0
        while True:
            try:
                question = self.driver.find_element(By.ID, f"interviewItem{i}")
                questions.append(question)
                i += 1
            except:
                break
        return questions
    
    def _process_questions(self, questions, url):
        """
        处理所有问题
        
        Args:
            questions: 问题元素列表
            url: 来源URL
            
        Returns:
            list: 处理结果列表
        """
        results = []
        
        for i in range(len(questions)):
            try:
                # 重新获取问题元素
                question = self.driver.find_element(By.ID, f"interviewItem{i}")
                title = question.text.strip() or f"问题 {i+1}"
                
                print(f"\n{'='*60}")
                print(f"正在处理第 {i+1}/{len(questions)} 个问题: {title}")
                print(f"{'='*60}")
                
                # 滚动并点击
                self._scroll_to_element(question)
                self._click_element(question)
                time.sleep(BUTTON_CLICK_WAIT)
                
                # 提取内容
                content = self._extract_question_content()
                
                if content:
                    result_data = {
                        'index': i + 1,
                        'title': title,
                        'question': content['question'],
                        'answer': content['answer']
                    }
                    results.append(result_data)
                    print(f"✓ 成功提取内容")
                    
                    # 立即保存
                    self.file_handler.save_question_as_markdown(result_data, url)
                else:
                    print(f"✗ 提取内容失败")
                    
            except Exception as e:
                print(f"处理问题 {i+1} 时出错: {e}")
                continue
        
        return results
    
    def _scroll_to_element(self, element):
        """滚动到元素位置"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(SCROLL_WAIT)
    
    def _click_element(self, element):
        """点击元素（支持JavaScript备用）"""
        try:
            element.click()
        except:
            self.driver.execute_script("arguments[0].click();", element)
    
    def _extract_question_content(self):
        """
        提取单个问题的内容
        
        Returns:
            dict: 包含question和answer的字典，失败返回None
        """
        try:
            print("  → 等待页面加载...")
            time.sleep(2)
            
            # 获取问题描述
            question_html = self._get_question_html()
            
            # 点击查看解题思路按钮
            self._click_answer_button()
            
            # 获取答案内容
            answer_html = self._get_answer_html()
            
            # 转换为Markdown
            question_text = self.converter.convert(question_html)
            answer_text = self.converter.convert(answer_html)
            
            result = {
                'question': question_text,
                'answer': answer_text
            }
            
            print(f"  ✓ 内容提取完成 - 问题:{len(question_text)}字 答案:{len(answer_text)}字")
            return result
            
        except Exception as e:
            print(f"提取内容时出错: {e}")
            return None
    
    def _get_question_html(self):
        """获取问题描述HTML"""
        for selector in QUESTION_DESC_SELECTORS:
            try:
                element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"  → 找到问题描述区域: {selector}")
                
                try:
                    content = element.find_element(By.CSS_SELECTOR, ".question-desc-content")
                    html = content.get_attribute('innerHTML')
                except:
                    html = element.get_attribute('innerHTML')
                
                print(f"  → 问题描述长度: {len(html)} 字符")
                return html
            except:
                continue
        
        return "未找到问题描述"
    
    def _click_answer_button(self):
        """查找并点击查看解题思路按钮"""
        print("  → 查找'查看解题思路'按钮...")
        
        try:
            button = None
            for selector in BUTTON_SELECTORS:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        elem_text = elem.text
                        if elem_text and any(keyword in elem_text for keyword in BUTTON_KEYWORDS):
                            button = elem
                            print(f"  → 找到按钮: '{elem_text}'")
                            break
                    if button:
                        break
                except:
                    continue
            
            if button:
                print("  → 正在点击按钮...")
                self._scroll_to_element(button)
                self._click_element(button)
                time.sleep(BUTTON_CLICK_WAIT)
                print("  ✓ 按钮点击成功，等待内容加载...")
            else:
                print("  ✗ 未找到按钮")
                
        except Exception as e:
            print(f"  ✗ 点击按钮时出错: {e}")
    
    def _get_answer_html(self):
        """获取答案内容HTML"""
        print("  → 提取答案内容...")
        
        try:
            time.sleep(2)
            answer_element = self.driver.find_element(By.CSS_SELECTOR, ".question-answer-wrap")
            
            # 尝试获取具体答案区域
            answer_html = ""
            try:
                answer_brief = answer_element.find_element(By.CSS_SELECTOR, ".answer-brief")
                answer_html = answer_brief.get_attribute('innerHTML')
            except:
                # 查找非隐藏的div
                answer_divs = answer_element.find_elements(By.CSS_SELECTOR, "div")
                for div in answer_divs:
                    style = div.get_attribute("style") or ""
                    if "display:none" not in style and "display: none" not in style:
                        if div.find_elements(By.TAG_NAME, "h2") or div.find_elements(By.TAG_NAME, "table"):
                            answer_html = div.get_attribute('innerHTML')
                            break
            
            if not answer_html:
                answer_html = answer_element.get_attribute('innerHTML')
            
            print(f"  → 答案长度: {len(answer_html)} 字符")
            return answer_html
            
        except Exception as e:
            print(f"  ✗ 提取答案失败: {e}")
            return "未找到答案内容"
    
    def close(self):
        """关闭浏览器"""
        self.driver.quit()
