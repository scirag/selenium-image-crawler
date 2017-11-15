# -*- coding: utf-8 -*-
from setuptools import setup

import sys
if sys.version_info < (3,3):
    sys.exit('Sorry, Python < 3.3 is not supported')

setup(name='imagecrawler',
      version='0.1',
      description='Selenium Image Crawler',
      url='https://github.com/scirag/selenium-image-crawler',
      author='Şafak ÇIRAĞ',
      author_email='safakcirag@gmail.com',
      license='MIT',
      packages=['crawler', 'processor'],
      install_requires=[
          'elasticsearch',
          'Pillow>=2.0',
          'requests',
          'imagehash',
          'selenium'
      ],
      zip_safe=False)
