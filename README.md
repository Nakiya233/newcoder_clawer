# 牛客网面试题爬虫

一个用于爬取牛客网面试题的Python爬虫工具，支持自动化浏览器操作、HTML到Markdown智能转换、多种输出格式。

## 功能特点

- ✅ 使用Selenium自动化浏览器操作
- ✅ 支持Cookie认证
- ✅ 自动点击"查看解题思路"按钮获取完整答案
- ✅ 输出Markdown格式文件，便于阅读和分享
- ✅ 爬取后立即保存，方便实时查看
- ✅ 自动生成目录索引
- ✅ HTML到Markdown智能转换（支持表格、代码块、列表等）
- ✅ 模块化设计，代码结构清晰，易于维护和扩展

## 环境要求

- Python 3.7+
- Chrome 浏览器
- Selenium 4.6+（自动管理ChromeDriver）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 准备Cookie文件

登录牛客网后，复制浏览器Cookie并保存到 `cookie.txt` 文件：

```
gr_user_id=xxx; NOWCODERUID=xxx; csrfToken=xxx; ...
```

### 2. 配置目标URL

编辑 `config.py` 中的 `TARGET_URLS`：

```python
TARGET_URLS = [
    "https://www.nowcoder.com/exam/interview/...",
]
```

### 3. 运行爬虫

```bash
python main.py
```

### 4. 查看结果

- `output/` 目录：包含所有题目的Markdown文件
- `output/README.md`：题目索引

## 项目结构

```
newcoder_claw/
├── main.py                    # 主入口文件
├── nowcoder_crawler.py        # 爬虫核心模块
├── html_converter.py          # HTML到Markdown转换模块
├── file_handler.py            # 文件保存处理模块
├── config.py                  # 配置管理模块
├── utils.py                   # 工具函数模块
├── cookie.txt                 # Cookie认证文件（需自行创建）
├── requirements.txt           # Python依赖
├── .gitignore                 # Git忽略文件
├── README.md                  # 项目说明
├── output/                    # 输出目录（自动创建）
│   ├── README.md              # 题目索引
│   └── *.md                   # 各个题目的Markdown文件
```

## 模块说明

### 📄 main.py - 主入口
程序启动入口，协调各模块完成爬取任务。

### 🕷️ nowcoder_crawler.py - 爬虫核心
爬虫主要逻辑，包含：
- 浏览器初始化和管理
- 页面导航和元素定位
- 问题内容提取
- Cookie设置和管理

### 🔄 html_converter.py - 格式转换
HTML到Markdown智能转换，支持：
- 标题（h1-h4）
- 代码块（自动识别并移除行号）
- 表格（普通表格和代码表格）
- 列表（有序/无序）
- 文本格式（加粗、斜体）
- 链接和图片
- 自动清理多余空格和HTML标签
- 移除"复制代码"等冗余文本

### 💾 file_handler.py - 文件处理
文件保存和管理，负责：
- 保存Markdown格式文件
- 生成索引目录文件
- 文件名安全处理

### ⚙️ config.py - 配置管理
集中配置管理，包含：
- 浏览器配置选项
- 等待时间配置
- CSS选择器配置
- 文件路径配置
- 目标URL列表

### 🔧 utils.py - 工具函数
通用工具函数：
- Cookie文件解析
- 文件名安全清理
- 目录自动创建

## 配置说明

所有配置项都在 `config.py` 中集中管理：

```python
# 爬虫配置
WAIT_TIMEOUT = 10              # 元素等待超时时间
PAGE_LOAD_WAIT = 5             # 页面加载等待时间
BUTTON_CLICK_WAIT = 3          # 点击按钮后等待时间

# 文件路径配置
OUTPUT_DIR = 'output'          # 输出目录
COOKIE_FILE = 'cookie.txt'     # Cookie文件路径

# 目标URL列表
TARGET_URLS = [
    "https://www.nowcoder.com/exam/interview/...",
]
```

## 输出格式示例

### Markdown格式（单个题目）

```markdown
# 1、请你说说Java基本数据类型和引用类型

**题号**: 1
**来源**: https://www.nowcoder.com/exam/interview/...
**爬取时间**: 2026-03-04 12:00:00

---

## 题目

1、请你说说Java基本数据类型和引用类型

---

## 解题思路

Java基本数据类型包括8种...

### 一、基本数据类型

| 类型 | 大小 | 默认值 | 取值范围 |
| --- | --- | --- | --- |
| byte | 1 | 0 | -128 ~ 127 |
...
```

## 版本说明

### v2.1（当前版本）- 精简优化
- ✅ 移除调试截图功能
- ✅ 仅保留Markdown输出，删除JSON和TXT格式
- ✅ 更简洁的输出结构
- 🚀 使用 `python main.py` 运行

### v2.0 - 模块化重构
- ✅ 模块化设计，代码结构清晰
- ✅ 配置集中管理
- ✅ 改进HTML转换逻辑
- ✅ 更好的错误处理
- 🚀 使用 `python main.py` 运行

### v1.0 - 单文件版本
- ⚠️ 已废弃，保留在 `crawler.py` 中供参考
- 可使用 `python crawler.py` 运行旧版本

## 常见问题

### Q: 如何获取Cookie?
A: 
1. 登录牛客网
2. 打开浏览器开发者工具（F12）
3. 切换到Network标签
4. 刷新页面，找到任意请求
5. 复制Request Headers中的Cookie值

### Q: Cookie多久过期？
A: Cookie有效期不定，如果爬取失败，尝试更新Cookie。

### Q: 如何修改爬取的URL？
A: 编辑 `config.py` 中的 `TARGET_URLS` 列表。

### Q: 如何调整等待时间？
A: 编辑 `config.py` 中的时间配置参数。

## 注意事项

- ⚠️ 请遵守网站的robots.txt和使用条款
- ⚠️ Cookie可能会过期，需要定期更新
- ⚠️ 仅供学习交流使用，请勿用于商业用途

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
