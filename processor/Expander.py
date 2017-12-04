from abc import ABC, abstractmethod

class Expander(ABC):
        @abstractmethod
        def expand(self, image):
            pass
