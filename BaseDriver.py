import os
import base64
import time
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import urllib.request
from multiprocessing import Pool


class BaseImageDriver(ABC):
    def __init__(self, search_key='', **kwargs):

        if type(search_key) == str:
            if search_key == '':
                search_key = 'kabe'
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

        ## file and folder path

        self.output_directory = kwargs.get('output_directory', './')
        self.process_count = kwargs.get('process_count', os.cpu_count())
        self.max_image_count = kwargs.get('max_image_count', 622)

        # google search specific url parameters
        self.search_url_prefix = None
        self.search_url_postfix = None

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
            self.downloading_all_photos()

    def downloading_all_photos(self):
        """ download all photos to particular folder

        """
        self.create_folder()
        pic_counter = 1

        thread_pool = Pool(processes=self.process_count)
        preview_urls = []
        original_urls = []
        pic_prefixes = []

        for preview_url, original_url in self.pic_url_list:
            pic_prefix_str = self.g_search_key + str(pic_counter)
            if preview_url:
                preview_urls.append(preview_url)
                original_urls.append(original_url)
                pic_prefixes.append(pic_prefix_str)
                pic_counter += 1

        thread_pool.map(self.download_single_image, zip(preview_urls, original_urls, pic_prefixes))
        thread_pool.close()
        thread_pool.join()

    def download_single_image(self, params):
        """ Download data according to the url link given.
            Args:
                url_link (str): url str.
                pic_prefix_str (str): pic_prefix_str for unique label the pic
        """
        preview_url, original_url, pic_prefix_str = params
        self.download_fault = 0
        file_ext = os.path.splitext(preview_url)[1]  # use for checking valid pic ext
        if len(file_ext) == 0:
            file_ext = ".png"
        temp_filename = pic_prefix_str + file_ext
        temp_filename_full_path = os.path.join(self.gs_raw_dirpath, temp_filename)

        valid_image_ext_list = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']  # not comprehensive

        #url = URL(url_link)
        #if url.redirect:
        #    return  # if there is re-direct, return

        if file_ext not in valid_image_ext_list:
            return  # return if not valid image extension
        # info_list = self.pic_info_list
        # info_list.append(pic_prefix_str + ': ' + url_link)

        info_txt_path = os.path.join(self.gs_raw_dirpath, self.g_search_key + '_info.txt')

        try:
            timeout = 1
            if preview_url.startswith("http://") or preview_url.startswith("https://"):
                raise
            with open(temp_filename_full_path, "wb") as fh:
                preview_url = preview_url[preview_url.find(",") + 1:]
                fh.write(base64.standard_b64decode(preview_url))
                with open(info_txt_path, 'a') as f:
                    f.write(pic_prefix_str + ': ' + original_url)
                    f.write('\n')

        except:
            # if self.__print_download_fault:
            try:
                response = urllib.request.urlopen(preview_url, data=None, timeout=timeout)
                data = response.read()  # a `bytes` object
                if len(data) > 0:
                    f = open(temp_filename_full_path, 'wb')  # save as test.gif
                    # print(url_link)
                    f.write(data)  # if have problem skip
                    f.close()
                    with open(info_txt_path, 'a') as f:
                        f.write(pic_prefix_str + ': ' + original_url)
                        f.write('\n')
            except:
                print('Problem with processing this data: ', original_url)
                self.download_fault = 1

    def create_folder(self):
        """
            Create a folder to put the log data segregate by date

        """
        self.gs_raw_dirpath = os.path.join(self.output_directory, time.strftime("_%d_%b%y", time.localtime()))
        if not os.path.exists(self.gs_raw_dirpath):
            os.makedirs(self.gs_raw_dirpath)

    def save_infolist_to_file(self):
        """ Save the info list to file.

        """
        temp_filename_full_path = os.path.join(self.gs_raw_dirpath, self.g_search_key + '_info.txt')

        with open(temp_filename_full_path, 'w') as f:
            for n in self.pic_info_list:
                f.write(n)
                f.write('\n')

