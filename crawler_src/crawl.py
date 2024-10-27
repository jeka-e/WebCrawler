
from argparse import ArgumentParser

from Crawler import Crawler

parser = ArgumentParser()
parser.add_argument("-u", "--url", dest="url", default=None,
                    help="single URL to parse", metavar="URL")
parser.add_argument("-l", "--list_url", dest="url_list", default=[],
                    help="list of URLs to parse", metavar="URLLIST")
parser.add_argument("-o", "--output_path", dest="output_path", default=None,
                    help="folder to store the output", metavar="OUTPUTPATH")

args = parser.parse_args()

if __name__ == "__main__":
    DEFAULT_OUTPUT_PATH = 'crawl_data'

    if args.output_path:
        output_path = args.output_path
    else:
        output_path = DEFAULT_OUTPUT_PATH

    crawler = Crawler(output_path)
    if args.url:
        crawler.crawl(args.url)

    elif args.url_list:
        f = open(args.url_list, 'r')
        urls = f.readlines()
        f.close()
        for url in urls:
            crawler.crawl(url)
            
    else:
        print('No URL provided')
