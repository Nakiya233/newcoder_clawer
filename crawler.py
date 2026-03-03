from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import json
import os

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
                    results.append({
                        'index': i + 1,
                        'title': title,
                        'question': content['question'],
                        'answer': content['answer']
                    })
                    print(f"✓ 成功提取内容")
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
                    question_text = question_element.text
                else:
                    question_text = "未找到问题描述"
                print(f"  → 问题描述长度: {len(question_text)} 字符")
            except:
                question_text = "未找到问题描述"
            
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
                
                # 获取所有display不为none的div
                answer_divs = answer_element.find_elements(By.CSS_SELECTOR, "div[style*='display']")
                answer_text = ""
                
                for div in answer_divs:
                    style = div.get_attribute("style")
                    if style and "display:none" not in style and "display: none" not in style:
                        text = div.text
                        if text and len(text) > 100:  # 找到实际内容
                            answer_text = text
                            break
                
                # 如果没找到，尝试直接获取整个区域
                if not answer_text:
                    # 尝试使用class="answer-brief"或其他答案class
                    try:
                        answer_text = answer_element.find_element(By.CSS_SELECTOR, ".answer-brief").text
                    except:
                        answer_text = answer_element.text
                
                print(f"  → 答案长度: {len(answer_text)} 字符")
                    
            except Exception as e:
                print(f"  ✗ 提取答案失败: {e}")
                answer_text = "未找到答案内容"
            
            result = {
                'question': question_text,
                'answer': answer_text
            }
            
            print(f"  ✓ 内容提取完成 - 问题:{len(question_text)}字 答案:{len(answer_text)}字")
            return result
            
        except Exception as e:
            print(f"提取内容时出错: {e}")
            return None
    
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
        
        print(f"\n✓ 爬取完成！共爬取 {len(all_results)} 个问题")
        print("结果已保存到:")
        print("  - nowcoder_questions.json (JSON格式)")
        print("  - nowcoder_questions.txt (文本格式)")
        
    except Exception as e:
        print(f"爬取过程出错: {e}")
    finally:
        crawler.close()


if __name__ == "__main__":
    main()
