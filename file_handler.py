"""
文件处理模块
"""
import os
from datetime import datetime
from utils import sanitize_filename


class FileHandler:
    """文件保存处理器"""
    
    def __init__(self, output_dir):
        """
        初始化文件处理器
        
        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = output_dir
    
    def save_question_as_markdown(self, question_data, source_url):
        """
        保存单个问题为Markdown文件
        
        Args:
            question_data: 问题数据字典，包含index, title, question, answer
            source_url: 来源URL
        """
        try:
            # 生成文件名
            index = question_data['index']
            title = question_data['title']
            safe_title = sanitize_filename(title)
            
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
    
    def generate_index_file(self, results):
        """
        生成Markdown索引文件
        
        Args:
            results: 结果列表
        """
        index_file = os.path.join(self.output_dir, 'README.md')
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("# 牛客网面试题库\n\n")
            f.write(f"**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**题目总数**: {len(results)}\n\n")
            f.write("---\n\n")
            f.write("## 题目列表\n\n")
            for item in results:
                safe_title = sanitize_filename(item['title'])
                filename = f"{item['index']:02d}_{safe_title}.md"
                f.write(f"{item['index']}. [{item['title']}]({filename})\n")
