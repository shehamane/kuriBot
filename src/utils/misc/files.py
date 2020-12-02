import os, time
from aiogram.types import PhotoSize


async def download_product_image(product_id, image: PhotoSize):
    dir_path = "../img/products/" + str(product_id)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    await image.download(dir_path + "/" + str(time.time()) + ".jpg")


async def get_product_images(product_id):
    dir_path = "../img/products/" + str(product_id)
    if not os.path.exists(dir_path):
        return False
    else:
        paths = []
        for file in os.listdir(dir_path):
            paths.append(dir_path + "/" + os.path.relpath(file))
        return paths
