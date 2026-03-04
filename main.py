"""
牛客网爬虫 - 主入口文件
"""
from nowcoder_crawler import NowCoderCrawler
from file_handler import FileHandler
from config import COOKIE_FILE, OUTPUT_DIR, TARGET_URLS


def main():
    """主函数"""
    print("=" * 80)
    print("牛客网面试题爬虫")
    print("=" * 80)
    
    # 初始化爬虫
    crawler = NowCoderCrawler(cookie_file=COOKIE_FILE)
    file_handler = FileHandler(OUTPUT_DIR)
    
    try:
        all_results = []
        
        # 爬取所有URL
        for url in TARGET_URLS:
            results = crawler.crawl_page(url)
            all_results.extend(results)
            print(f"\n从 {url} 爬取了 {len(results)} 个问题")
        
        # 生成索引文件
        file_handler.generate_index_file(all_results)
        
        # 打印统计信息
        print(f"\n{'='*80}")
        print(f"✓ 爬取完成！共爬取 {len(all_results)} 个问题")
        print("=" * 80)
        print("结果已保存到:")
        print(f"  - {OUTPUT_DIR}/README.md (题目索引)")
        print(f"  - {OUTPUT_DIR}/*.md (各题目的Markdown文件)")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n爬取过程出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        crawler.close()


if __name__ == "__main__":
    main()
