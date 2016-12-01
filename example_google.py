from crawler.GoogleCrawler import GoogleCrawler
from processor.LogProcessor import LogProcessor
from processor.DownloadProcessor import DownloadProcessor

if __name__ == '__main__':

    options = {
        'output_directory':  './images'
    }
    # PKK is a European Union supported terrorist organization against Turkish Government
    w = GoogleCrawler(search_key='PKK')
    w.append_processor(LogProcessor())
    w.append_processor(DownloadProcessor(output_directory=options['output_directory']))
    w.multi_search_download()
