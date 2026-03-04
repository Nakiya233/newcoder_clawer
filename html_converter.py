"""
HTML到Markdown转换模块
"""
import re
import html


class HTMLToMarkdownConverter:
    """HTML到Markdown转换器"""
    
    @staticmethod
    def convert(html_content):
        """
        将HTML内容转换为Markdown格式
        
        Args:
            html_content: HTML内容字符串
            
        Returns:
            str: Markdown格式的内容
        """
        if not html_content:
            return ""
        
        # 解码HTML实体
        content = html.unescape(html_content)
        
        # 转换表格
        content = HTMLToMarkdownConverter._convert_tables(content)
        
        # 转换标题
        content = HTMLToMarkdownConverter._convert_headings(content)
        
        # 转换代码块
        content = HTMLToMarkdownConverter._convert_code_blocks(content)
        
        # 转换列表
        content = HTMLToMarkdownConverter._convert_lists(content)
        
        # 转换文本格式
        content = HTMLToMarkdownConverter._convert_text_formatting(content)
        
        # 转换链接
        content = HTMLToMarkdownConverter._convert_links(content)
        
        # 转换图片
        content = HTMLToMarkdownConverter._convert_images(content)
        
        # 转换段落和换行
        content = HTMLToMarkdownConverter._convert_paragraphs(content)
        
        # 移除其他HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 移除"复制代码"文本
        content = HTMLToMarkdownConverter._remove_copy_code_text(content)
        
        # 清理空格和空行
        content = HTMLToMarkdownConverter._clean_whitespace(content)
        
        return content.strip()
    
    @staticmethod
    def _convert_headings(content):
        """转换标题 (h1-h4)"""
        content = re.sub(
            r'<h1[^>]*>(.*?)</h1>',
            lambda m: f"\n# {' '.join(re.sub(r'<[^>]+>', '', m.group(1)).split())}\n",
            content, flags=re.DOTALL
        )
        content = re.sub(
            r'<h2[^>]*>(.*?)</h2>',
            lambda m: f"\n## {' '.join(re.sub(r'<[^>]+>', '', m.group(1)).split())}\n",
            content, flags=re.DOTALL
        )
        content = re.sub(
            r'<h3[^>]*>(.*?)</h3>',
            lambda m: f"\n### {' '.join(re.sub(r'<[^>]+>', '', m.group(1)).split())}\n",
            content, flags=re.DOTALL
        )
        content = re.sub(
            r'<h4[^>]*>(.*?)</h4>',
            lambda m: f"\n#### {' '.join(re.sub(r'<[^>]+>', '', m.group(1)).split())}\n",
            content, flags=re.DOTALL
        )
        return content
    
    @staticmethod
    def _convert_code_blocks(content):
        """转换代码块"""
        content = re.sub(
            r'<pre[^>]*><code[^>]*>(.*?)</code></pre>',
            r'\n```\n\1\n```\n',
            content, flags=re.DOTALL
        )
        content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', content, flags=re.DOTALL)
        return content
    
    @staticmethod
    def _convert_lists(content):
        """转换列表"""
        content = re.sub(r'<ul[^>]*>', r'\n', content)
        content = re.sub(r'</ul>', r'\n', content)
        content = re.sub(r'<ol[^>]*>', r'\n', content)
        content = re.sub(r'</ol>', r'\n', content)
        
        # 处理列表项
        li_items = re.findall(r'<li[^>]*>(.*?)</li>', content, flags=re.DOTALL)
        for i, item in enumerate(li_items, 1):
            clean_item = re.sub(r'<[^>]+>', '', item)
            clean_item = ' '.join(clean_item.split())
            # 尝试替换原始的li标签
            content = content.replace(
                f'<li{content[content.find("<li"):content.find(">", content.find("<li"))+1-3]}>{item}</li>',
                f'{i}. {clean_item}\n',
                1
            )
        
        # 清理剩余的li标签
        content = re.sub(
            r'<li[^>]*>(.*?)</li>',
            lambda m: f"- {' '.join(re.sub(r'<[^>]+>', '', m.group(1)).split())}\n",
            content, flags=re.DOTALL
        )
        return content
    
    @staticmethod
    def _convert_text_formatting(content):
        """转换文本格式（加粗、斜体）"""
        content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL)
        content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', content, flags=re.DOTALL)
        content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content, flags=re.DOTALL)
        content = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', content, flags=re.DOTALL)
        return content
    
    @staticmethod
    def _convert_links(content):
        """转换链接"""
        # 先移除"复制代码"链接
        content = re.sub(r'<a[^>]*href=["\']#["\'][^>]*>复制代码</a>', '', content)
        # 转换其他链接
        content = re.sub(
            r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>',
            r'[\2](\1)',
            content, flags=re.DOTALL
        )
        return content
    
    @staticmethod
    def _convert_images(content):
        """转换图片"""
        content = re.sub(
            r'<img[^>]*src=["\']([^"\']*)["\'][^>]*alt=["\']([^"\']*)["\'][^>]*>',
            r'![\2](\1)',
            content
        )
        content = re.sub(r'<img[^>]*src=["\']([^"\']*)["\'][^>]*>', r'![](\1)', content)
        return content
    
    @staticmethod
    def _convert_paragraphs(content):
        """转换段落和换行"""
        content = re.sub(r'<br\s*/?>', r'\n', content)
        content = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\1\n', content, flags=re.DOTALL)
        content = re.sub(r'<div[^>]*>(.*?)</div>', r'\1\n', content, flags=re.DOTALL)
        return content
    
    @staticmethod
    def _remove_copy_code_text(content):
        """移除各种形式的"复制代码"文本"""
        content = re.sub(r'\[?复制代码\]?\s*\(#\)', '', content)
        content = re.sub(r'^\s*复制代码\s*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'复制代码\s*\n', '\n', content)
        return content
    
    @staticmethod
    def _clean_whitespace(content):
        """清理空格和空行"""
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
        return content
    
    @staticmethod
    def _convert_tables(html_content):
        """将HTML表格转换为Markdown表格格式"""
        def table_replacer(match):
            table_html = match.group(0)
            
            # 检查是否为代码表格
            if 'class="gutter"' in table_html or 'class="code"' in table_html:
                return HTMLToMarkdownConverter._convert_code_table(table_html)
            
            # 正常表格处理
            return HTMLToMarkdownConverter._convert_normal_table(table_html)
        
        result = re.sub(r'<table[^>]*>.*?</table>', table_replacer, html_content, flags=re.DOTALL)
        return result
    
    @staticmethod
    def _convert_code_table(table_html):
        """转换代码表格（带行号的代码块）"""
        code_lines = []
        code_divs = re.findall(
            r'<div[^>]*class="[^"]*line[^"]*"[^>]*>(.*?)</div>',
            table_html, flags=re.DOTALL
        )
        
        for line in code_divs:
            # 跳过行号div
            if re.search(r'class="[^"]*number\d+[^"]*"', line) and '<code' not in line:
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
            # 移除每行开头的行号
            cleaned_lines = []
            for line in code_lines:
                line = re.sub(r'^\s*\d+\s*$', '', line)
                line = re.sub(r'^\s*\d+\s+', '', line)
                if line.strip():
                    cleaned_lines.append(line)
            
            return '\n\n```java\n' + '\n'.join(cleaned_lines) + '\n```\n\n'
        
        return ''
    
    @staticmethod
    def _convert_normal_table(table_html):
        """转换普通HTML表格"""
        # 提取表头
        headers = re.findall(r'<th[^>]*>(.*?)</th>', table_html, flags=re.DOTALL)
        if not headers:
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
            if '<th' in row:
                continue
            
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, flags=re.DOTALL)
            cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
            
            if cells and len(cells) == len(headers):
                markdown_table.append('| ' + ' | '.join(cells) + ' |')
        
        return '\n' + '\n'.join(markdown_table) + '\n'
