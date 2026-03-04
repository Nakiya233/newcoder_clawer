"""
配置管理模块
"""

# 浏览器配置
CHROME_OPTIONS = [
    '--disable-blink-features=AutomationControlled',
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
]

# 爬虫配置
WAIT_TIMEOUT = 10  # WebDriverWait 超时时间(秒)
PAGE_LOAD_WAIT = 5  # 页面加载等待时间(秒)
BUTTON_CLICK_WAIT = 3  # 点击按钮后等待时间(秒)
SCROLL_WAIT = 0.5  # 滚动后等待时间(秒)

# 文件路径配置
COOKIE_FILE = 'cookie.txt'
OUTPUT_DIR = 'output'
INDEX_FILE_NAME = 'README.md'

# 选择器配置
QUESTION_LIST_SELECTORS = [
    ".question-list",
    "[class*='question-list']",
    "div.interview-left-aside",
    ".el-scrollbar__wrap"
]

QUESTION_DESC_SELECTORS = [
    ".question-desc",
    "[class*='question-desc']",
    ".main-content"
]

BUTTON_SELECTORS = [
    "[class*='tw-bg-green-500']",
    ".tw-bg-green-500",
    "div[class*='tw-cursor-pointer'][class*='tw-bg-green']"
]

BUTTON_KEYWORDS = ['查看', '解题', '思路']

# 网站配置
DOMAIN = 'www.nowcoder.com'
BASE_URL = f'https://{DOMAIN}'
COOKIE_DOMAIN = f'.{DOMAIN}'

# 目标URL列表
TARGET_URLS = [
    "https://www.nowcoder.com/exam/interview/94883707/test?paperId=61536918&input=java&order=0",
]
