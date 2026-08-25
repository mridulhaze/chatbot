import argparse
from .config import load_config
from .crawler import NUCrawler

def main():
    parser = argparse.ArgumentParser(description="NU website knowledge crawler")
    parser.add_argument("--config",default="config.yaml")
    parser.add_argument("--max-pages",type=int,default=None)
    parser.add_argument("--delay",type=float,default=None)
    parser.add_argument("--no-robots",action="store_true")
    args=parser.parse_args()

    config=load_config(args.config)
    if args.max_pages is not None:
        config["crawl"]["max_pages"]=args.max_pages
    if args.delay is not None:
        config["crawl"]["delay_seconds"]=args.delay
    if args.no_robots:
        config["crawl"]["respect_robots"]=False

    crawler=NUCrawler(config)
    try:
        crawler.run()
    finally:
        crawler.close()

if __name__=="__main__":
    main()
