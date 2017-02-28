# selenium-image-crawler
Selenium Image Crawler

Reference source code : https://simply-python.com/2015/05/18/saving-images-from-google-search-using-selenium-and-python/

**Dependencies**
* python>=3.3
* elasticsearch
* Pillow>=2.0
* requests
* imagehash
* selenium

Selenium Driver : PhantomJS (headless browser)
To Install PhantomJS follow https://gist.github.com/leommoore/f3d7f2ff1fea6e69ee70da1beb72b0e1


**Now:**
* Google Image Searh and Yandex Image Search included
* BaseCrawler supplied for other search engines or websites
* GoogleCrawler and YandexCrawler extended from BaseCrawler
* BaseProcessor supplied for processing of each search item
* LogProcessor, DownloadProcessor and ElasticSearchProcessor extended from BaseProcessor
* DownloadProcessor, ElasticSearchProcessor : Pool class is used from multiprocessing library for parallelizing download
* example_*.py files are included for simple usage

**Next:**
* More drivers will be developed : Bing Image Search
* Result images and metadata will be stored in databases : MongoDB, Cassandra, PostgreSQL
