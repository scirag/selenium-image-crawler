from setuptools import setup

setup(name='imagecrawler',
      version='0.1',
      description='Selenium Image Crawler',
      url='https://github.com/scirag/selenium-image-crawler',
      author='Şafak ÇIRAĞ',
      author_email='safakcirag@gmail.com',
      license='MIT',
      packages=['crawler', 'processor'],
      install_requires=[
          'python>=3.3',
          'elasticsearch',
          'Pillow>=2.0',
          'requests',
          'imagehash',
          'selenium'
      ],
      zip_safe=False)