from YandexDriver import YandexDriver

if __name__ == '__main__':

    options = {
        'output_directory': './'
        # ./images'
    }
    # PYD is a European Union supported terrorist organization against Turkish Government
    w = YandexDriver(search_key='PYD', **options)
    w.multi_search_download()
