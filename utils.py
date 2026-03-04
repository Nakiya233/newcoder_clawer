"""
工具函数模块
"""
import os


def load_cookies(cookie_file):
    """
    从文件读取cookie
    
    Args:
        cookie_file: cookie文件路径
        
    Returns:
        dict: cookie字典
    """
    with open(cookie_file, 'r', encoding='utf-8') as f:
        cookie_str = f.read().strip()
    
    cookies = {}
    for item in cookie_str.split('; '):
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key] = value
    return cookies


def sanitize_filename(title, max_length=50):
    """
    清理文件名中的非法字符
    
    Args:
        title: 原始标题
        max_length: 最大长度
        
    Returns:
        str: 清理后的安全文件名
    """
    allowed_chars = ' -_（）。，'
    safe_title = "".join(c for c in title if c.isalnum() or c in allowed_chars).strip()
    return safe_title[:max_length]


def ensure_directory(directory):
    """
    确保目录存在，不存在则创建
    
    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"✓ 创建输出目录: {directory}")
