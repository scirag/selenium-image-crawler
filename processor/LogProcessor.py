from .BaseProcessor import BaseProcessor


class LogProcessor(BaseProcessor):

    def setup(self):
        pass

    def process(self, preview_image_url, original_image_url, search_term):
        print("search term:%s, preview: %s, original: %s" % (search_term, preview_image_url, original_image_url))

    def teardown(self):
        pass

