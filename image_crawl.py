# -*- coding: utf-8 -*-
# author: John Poplett

import argparse
import os
import sys

from crawler.GoogleCrawler import GoogleCrawler
from crawler.YandexCrawler import YandexCrawler
from processor.LogProcessor import LogProcessor
from processor.DownloadProcessor import DownloadProcessor

# Lookup-table for crawler constructors.
crawlers = {
    'google' : GoogleCrawler,
    'yandex' : YandexCrawler
}

# Lookup-table for processor constructors. Each constructor takes
# the value "args".
processors = {
    'download': lambda args: DownloadProcessor(output_directory = args.output_directory, process_count = args.process_count),
    'elastic': lambda args: ElasticSearchProcessor(process_count = args.process_count),
    'log': lambda args: LogProcessor()
}

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--crawler', nargs='+',
        choices=('google', 'yandex'),
        help='specify crawler(s) to use')
    parser.add_argument('--debug', action="store_true", default=False,
        help='debug argument processing')
    parser.add_argument('--max-image-count', type=int, default=200,
        help='maximum number of images to download per search term')
    parser.add_argument('--output-directory', type=str, default=os.path.join('.', 'images'),
        help='specify download directory')
    parser.add_argument('--process-count', type=int, default=os.cpu_count(),
        help='number of CPUs to use for processing')
    parser.add_argument('--processor', type=str, nargs='+',
        choices=('download', 'elastic', 'log'),
        help='specify processor(s) to use')
    parser.add_argument('--search-terms-file', type=str,
        help='a text file with a list of search terms')
    parser.add_argument('search_terms', type=str, nargs='*',
        help='search terms')
    args = parser.parse_args()

    if args.search_terms_file:
        with open(args.search_terms_file, 'r') as f:
            search_terms = [search_term.strip() for search_term in f.readlines()]
            args.search_terms.extend(search_terms)

    if args.crawler == None:
        args.crawler = ['google']

    if args.processor == None:
        args.processor = ['download']

    if args.debug:
        print(args)
        sys.exit(1)

    # Run each specified crawler in sequence
    for Crawler in [crawlers[crawler] for crawler in args.crawler]:
        w = Crawler(max_image_count = args.max_image_count)
        for Processor in [processors[processor] for processor in args.processor]:
            w.append_processor(Processor(args))
        w.run(args.search_terms)

    sys.exit(0)
