from abc import ABC, abstractmethod


class BaseProcessor(ABC):

    @abstractmethod
    def before_process(self):
        pass

    @abstractmethod
    def process(self, preview_image_url, original_image_url, search_term):
        pass

    @abstractmethod
    def after_process(self):
        pass
