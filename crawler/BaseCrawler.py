import os
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class BaseCrawler(ABC):
    def __init__(self, **kwargs):

        ## storage
        self.pic_url_list = []
        self.pic_info_list = []

        self.max_image_count = kwargs.get('max_image_count', 622)

        self.processor_list = []

    @staticmethod
    def reformat_search_for_spaces(search_term):
        return search_term.strip().replace(' ', '+')

    def set_max_image_count(self, num_image):
        """ Set the number of image to download. Set to self.image_dl_per_search.
            Args:
                num_image (int): num of image to download.
        """
        self.max_image_count = num_image

    def append_processor(self, processor):
        self.processor_list.append(processor)

    def formed_search_url(self, search):
        ''' Form the url either one selected key phrases or multiple search items and return result.
        '''
        return self.get_search_url_prefix() + BaseCrawler.reformat_search_for_spaces(search) + self.get_search_url_suffix()

    def create_selenium_driver(self):
        # driver = webdriver.Chrome()
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"
        )
        driver = webdriver.PhantomJS(desired_capabilities=dcap)
        driver.set_window_size(1024, 768)
        return driver

    @abstractmethod
    def get_search_url_prefix(self):
        pass

    @abstractmethod
    def get_search_url_suffix(self):
        pass

    @abstractmethod
    def load_page(self, driver, target_url):
        pass

    @abstractmethod
    def extract_pic_url(self, driver):
        driver.quit()

    def run(self, search_key_list):
        if type(search_key_list) == str:
            search_key_list = [search_key_list]

        if type(search_key_list) != list:
            print('search_keyword not of type str or list')
            raise

        for search in search_key_list:
            self.pic_url_list = []
            self.pic_info_list = []
            target_url = self.formed_search_url(search)
            driver = self.create_selenium_driver()
            self.load_page(driver, target_url)
            self.extract_pic_url(driver)
            self.process_all_images(search)

    def process_all_images(self, search_term):

        for processor in self.processor_list:
            processor.before_process(search_term)

        if self.max_image_count < len(self.pic_url_list):
            self.pic_url_list = self.pic_url_list[:self.max_image_count]

        for preview_url, original_url in self.pic_url_list:
            for processor in self.processor_list:
                processor.process(preview_url, original_url, search_term)

        for processor in self.processor_list:
            processor.after_process(search_term)
