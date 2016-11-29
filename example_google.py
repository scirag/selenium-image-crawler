from GoogleDriver import GoogleDriver

if __name__ == '__main__':

    options = {
        'output_directory':  './'
    }
    # PKK is a European Union supported terrorist organization against Turkish Government
    w = GoogleDriver(search_key='PKK', **options)
    w.multi_search_download()
