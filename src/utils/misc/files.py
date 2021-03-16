import os
import shutil

from aiogram.types import PhotoSize


async def gen_img_files():
    dir_path = "img/products"
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    if not os.path.exists("img/catalog.png"):
        shutil.copyfile("img/default.png", "img/catalog.png")
    if not os.path.exists("img/cart.png"):
        shutil.copyfile("img/default.png", "img/cart.png")


async def download_product_image(product_id, image: PhotoSize):
    dir_path = "img/products/" + str(product_id)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    await image.download(dir_path + "/" + str("MAIN.jpg"))


async def delete_product_image(product_id):
    dir_path = "img/products/" + str(product_id)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        return 0
    return 1


async def get_product_image_path(product_id):
    dir_path = "img/products/" + str(product_id)
    if not os.path.exists(dir_path):
        return False
    else:
        img_path = os.listdir(dir_path)[0]
        path = dir_path + "/" + os.path.relpath(img_path)
        return path


async def download_image(path, image: PhotoSize):
    path = 'img/' + path
    await image.download(path)
