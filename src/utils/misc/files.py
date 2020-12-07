import os, time
from aiogram.types import PhotoSize


async def download_product_image(product_id, image: PhotoSize):
    dir_path = "../img/products/" + str(product_id)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    await image.download(dir_path + "/" + str(time.time()) + ".jpg")


async def get_product_image_path(product_id):
    dir_path = "../img/products/" + str(product_id)
    if not os.path.exists(dir_path):
        return False
    else:
        img_path = os.listdir(dir_path)[0]
        path = dir_path + "/" + os.path.relpath(img_path)
        return path
