import os
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class BaseCrawler(ABC):
    def __init__(self, search_key='', **kwargs):

        if type(search_key) == str:
            if search_key == '':
                search_key = 'Kabe'
            self.g_search_key_list = [search_key]
        elif type(search_key) == list:
            self.g_search_key_list = search_key
        else:
            print('search_keyword not of type str or list')
            raise

        self.g_search_key = ''
        self.target_url_str = ''

        ## storage
        self.pic_url_list = []
        self.pic_info_list = []

        self.process_count = kwargs.get('process_count', os.cpu_count())
        self.max_image_count = kwargs.get('max_image_count', 622)

        # google search specific url parameters
        self.search_url_prefix = None
        self.search_url_postfix = None

        self.processor_list = []

    def reformat_search_for_spaces(self):
        """
            Method call immediately at the initialization stages
            get rid of the spaces and replace by the "+"
            Use in search term. Eg: "Cookie fast" to "Cookie+fast"

            steps:
            strip any lagging spaces if present
            replace the self.g_search_key
        """
        self.g_search_key = self.g_search_key.rstrip().replace(' ', '+')

    def set_max_image_count(self, num_image):
        """ Set the number of image to download. Set to self.image_dl_per_search.
            Args:
                num_image (int): num of image to download.
        """
        self.max_image_count = num_image

    def append_processor(self, processor):
        self.processor_list.append(processor)

    def formed_search_url(self):
        ''' Form the url either one selected key phrases or multiple search items.
            Get the url from the self.g_search_key_list
            Set to self.sp_search_url_list
        '''
        self.reformat_search_for_spaces()
        self.target_url_str = self.search_url_prefix + self.g_search_key + self.search_url_postfix

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
    def load_page(self, driver):
        pass

    @abstractmethod
    def extract_pic_url(self, driver):
        driver.quit()

    def multi_search_download(self):
        """ Mutli search download"""
        for search in self.g_search_key_list:
            self.pic_url_list = []
            self.pic_info_list = []
            self.g_search_key = search
            self.formed_search_url()
            driver = self.create_selenium_driver()
            self.load_page(driver)
            self.extract_pic_url(driver)
            self.process_all_images()

    def process_all_images(self):

        for processor in self.processor_list:
            processor.setup()

        search_term = self.g_search_key.rstrip()
        for preview_url, original_url in self.pic_url_list:
            processor.process(preview_url, original_url, search_term)

        for processor in self.processor_list:
            processor.teardown()

    def save_infolist_to_file(self):
        """ Save the info list to file.

        """
        temp_filename_full_path = os.path.join(self.gs_raw_dirpath, self.g_search_key + '_info.txt')

        with open(temp_filename_full_path, 'w') as f:
            for n in self.pic_info_list:
                f.write(n)
                f.write('\n')

