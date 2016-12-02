from .BaseProcessor import BaseProcessor
from elasticsearch import Elasticsearch
from PIL import Image
from io import BytesIO
import imagehash
import base64
import json
import uuid
from multiprocessing import Pool
import requests
import os

es = Elasticsearch()


def create_index(index_name):
    es.indices.create(index_name, ignore=400)


def generate_guid():
    return str(uuid.uuid4())


def index_image(image, file_name, index_name, metadata):
    preview_image_url, original_image_url, search_term = metadata
    image_hash = imagehash.phash(image, hash_size=16)
    thumbnail_size = 128, 128
    image.thumbnail(thumbnail_size)
    output = BytesIO()
    image.save(output, format="JPEG", quality=66, optimize=True)
    img_base64 = base64.b64encode(output.getvalue())
    output.close()
    uid = generate_guid()
    json_data = json.dumps({
        'hash': str(image_hash),
        'fileName': file_name,
        'imgBase64': img_base64.decode(),
        'metadata': {
            'preview': preview_image_url,
            'original': original_image_url,
            'searchTerm': search_term
        }
    })
    es.index(index=index_name, doc_type='image_info', id=uid, body=json_data)


def get_image_from_url(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image


def index_image_es(metadata):
    preview_image_url, original_image_url, search_term, index_name = metadata
    image = None
    if preview_image_url is None:
        return
    if preview_image_url.startswith("data:"):
        pass
        # data = preview_image_url[preview_image_url.find(",")+1:]
        # data = base64.b64decode(data)
        # Image.fromstring()
        # image = Image.open(data)
    elif preview_image_url.startswith("https://encrypted"):
        image = get_image_from_url(preview_image_url)

    if image is not None:
        chunk = original_image_url.split("/")
        file_name = chunk[len(chunk)-1]
        metadata = (preview_image_url, original_image_url, search_term)
        try:
            index_image(image=image, file_name=file_name, index_name=index_name, metadata=metadata)
        except Exception as ex:
            print(ex)
            pass


class ElasticSearchProcessor(BaseProcessor):

    def __init__(self, process_count=os.cpu_count()):
        self.index_name = 'cebir'
        self.document_type = 'image_info'
        self.process_count = process_count
        self.preview_image_urls = []
        self.original_image_urls = []
        self.search_terms = []
        self.index_names = []

    def before_process(self):
        create_index(self.index_name)
        self.preview_image_urls = []
        self.original_image_urls = []
        self.search_terms = []
        self.index_names = []

    def process(self, preview_image_url, original_image_url, search_term):
        if preview_image_url:
            self.preview_image_urls.append(preview_image_url)
            self.original_image_urls.append(original_image_url)
            self.search_terms.append(search_term)
            self.index_names.append(self.index_name)

    def after_process(self):
        thread_pool = Pool(processes=self.process_count)
        thread_pool.map(index_image_es, zip(self.preview_image_urls,
                                            self.original_image_urls,
                                            self.search_terms,
                                            self.index_names))
        thread_pool.close()
        thread_pool.join()
