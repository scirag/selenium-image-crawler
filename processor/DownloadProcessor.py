from .BaseProcessor import BaseProcessor
from multiprocessing import Pool
import os
import hashlib
import urllib.request
import time
import base64


class DownloadProcessor(BaseProcessor):

    def __init__(self, output_directory='./', process_count=os.cpu_count()):
        self.output_directory = output_directory
        self.process_count = process_count

    def before_process(self, search_term):

        #
        # Create folder for downloads based on search term.
        #
        self.gs_raw_dirpath = os.path.join(self.output_directory, search_term.strip().replace(' ', '_'))
        if not os.path.exists(self.gs_raw_dirpath):
            os.makedirs(self.gs_raw_dirpath)

        self.preview_urls = []
        self.original_urls = []
        self.search_terms = []

    def process(self, preview_image_url, original_image_url, search_term):
        if preview_image_url:
            self.preview_urls.append(preview_image_url)
            self.original_urls.append(original_image_url)
            self.search_terms.append(search_term.strip().replace(' ', '_'))

    def download_single_image(self, params):
        """ Download data according to the url link given.
            Args:
                url_link (str): url str.
                pic_prefix_str (str): pic_prefix_str for unique label the pic
        """
        preview_url, original_url, search_term = params
        self.download_fault = 0

        timeout = 1
        if preview_url.startswith("http://") or preview_url.startswith("https://"):
            try:
                response = urllib.request.urlopen(preview_url, data=None, timeout=timeout)
                if response.headers['Content-Type'] == "image/jpeg":
                    file_ext = ".jpg"
                elif response.headers['Content-Type'] == "image/png":
                    file_ext = ".png"
                elif response.headers['Content-Type'] == "image/gif":
                    file_ext = ".gif"
                else:
                    raise "image format not found"
                data = response.read()  # a `bytes` object
                if len(data) > 0:
                    md5_key = hashlib.md5(data).hexdigest()
                    pic_prefix_str = '%s.%s' % (search_term, md5_key)
                    temp_filename = pic_prefix_str + file_ext
                    temp_filename_full_path = os.path.join(self.gs_raw_dirpath, temp_filename)
                    # If file exists, could be rare MD5 collision or, more likely,
                    # is the same exact image downloaded from a different location
                    if not os.path.exists(temp_filename_full_path):
                        info_txt_path = os.path.join(self.gs_raw_dirpath, search_term + '_info.txt')
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
            pass
        elif preview_url.startswith("data:"):
            if preview_url.startswith("data:image/jpeg"):
                file_ext = ".jpg"
            elif preview_url.startswith("data:image/png"):
                file_ext = ".png"
            elif preview_url.startswith("data:image/gif"):
                file_ext = ".gif"
            else:
                raise "image format not found"
            data = base64.standard_b64decode(preview_url)
            if len(data) > 0:
                md5_key = hashlib.md5(data).hexdigest()
                pic_prefix_str = '%s.%s' % (search_term, md5_key)
                temp_filename = pic_prefix_str + file_ext
                temp_filename_full_path = os.path.join(self.gs_raw_dirpath, temp_filename)
                if not os.path.exists(temp_filename_full_path):
                    info_txt_path = os.path.join(self.gs_raw_dirpath, search_term + '_info.txt')
                    with open(temp_filename_full_path, "wb") as fh:
                        preview_url = preview_url[preview_url.find(",") + 1:]
                        fh.write(base64.standard_b64decode(preview_url))
                        with open(info_txt_path, 'a') as f:
                            f.write(pic_prefix_str + ': ' + original_url)
                            f.write('\n')

    def after_process(self, search_term):
        thread_pool = Pool(processes=self.process_count)
        thread_pool.map(self.download_single_image, zip(self.preview_urls, self.original_urls, self.search_terms))
        thread_pool.close()
        thread_pool.join()
