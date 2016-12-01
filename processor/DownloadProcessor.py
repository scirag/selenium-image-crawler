from .BaseProcessor import BaseProcessor
from multiprocessing import Pool
import os
import urllib.request
import time
import base64


class DownloadProcessor(BaseProcessor):

    def __init__(self, output_directory='./', process_count=os.cpu_count()):
        self.output_directory = output_directory
        self.process_count = process_count

    def setup(self):
        self.create_folder()
        self.pic_counter = 1

        self.preview_urls = []
        self.original_urls = []
        self.pic_prefixes = []

    def process(self, preview_image_url, original_image_url, search_term):
        self.search_term = search_term
        pic_prefix_str = search_term + str(self.pic_counter)
        if preview_image_url:
            self.preview_urls.append(preview_image_url)
            self.original_urls.append(original_image_url)
            self.pic_prefixes.append(pic_prefix_str)
            self.pic_counter += 1

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

        info_txt_path = os.path.join(self.gs_raw_dirpath, self.search_term + '_info.txt')

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

    def teardown(self):
        thread_pool = Pool(processes=self.process_count)
        thread_pool.map(self.download_single_image, zip(self.preview_urls, self.original_urls, self.pic_prefixes))
        thread_pool.close()
        thread_pool.join()
