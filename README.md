# 牛客网面试题爬虫

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 确保 `cookie.txt` 文件包含有效的登录cookie
2. 编辑 `crawler.py` 中的 `urls` 列表，添加需要爬取的页面URL
3. 运行爬虫：

```bash
python crawler.py
```

## 输出文件

- `nowcoder_questions.json` - JSON格式的结构化数据
- `nowcoder_questions.txt` - 易读的文本格式

## 功能特性

- ✓ 自动加载cookie进行认证
- ✓ 遍历问题列表
- ✓ 自动点击"查看解题思路"按钮
- ✓ 提取问题描述和答案
- ✓ 支持批量爬取多个页面
- ✓ 保存为多种格式

## 注意事项

- 请遵守网站使用条款，合理控制爬取频率
- cookie可能会过期，需要定期更新
- 如遇到反爬，可适当增加延时时间
