from YandexDriver import YandexDriver

if __name__ == '__main__':

    options = {
        'output_directory': r"F:\PROJELER\cebir\veri\teror"
        # ./images'
    }
    w = YandexDriver(search_key='PKK', **options)
    w.set_max_image_count(200)
    w.multi_search_download()
