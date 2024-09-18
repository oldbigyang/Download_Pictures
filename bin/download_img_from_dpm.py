#!/usr/bin/env python
# encoding: utf-8

import os
import requests
from PIL import Image
from io import BytesIO
import logging
from tqdm import tqdm
from datetime import datetime

def setup_logging(log_dir='logs'):
    os.makedirs(log_dir, exist_ok=True)
    log_filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.log'
    log_path = os.path.join(log_dir, log_filename)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=log_path,
        filemode='w'
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)

    return log_path

def download_and_stitch_images(base_url, image_pattern, max_rows, max_cols, save_directory='/home/hongdayang/work/dw_img/images', stitched_image_name='stitched_image.png'):
    try:
        # 设置日志
        log_dir = '/home/hongdayang/work/Download_Pictures/logs'
        log_path = setup_logging(log_dir)

        # 确保保存目录存在
        os.makedirs(save_directory, exist_ok=True)

        images = []
        with tqdm(total=max_rows * max_cols, desc='Downloading images', unit='image') as progress_bar:
            for row in range(max_rows):
                row_images = []
                for col in range(max_cols):
                    img_url = base_url + image_pattern.format(row=row, col=col)
                    try:
                        img_response = requests.get(img_url, timeout=10)
                        if img_response.status_code == 200:
                            img = Image.open(BytesIO(img_response.content))
                            row_images.append(img)
                            logging.info(f"Downloaded image {img_url}")
                        else:
                            logging.info(f"Image not found: {img_url}")
                    except requests.exceptions.RequestException as e:
                        logging.error(f"Error fetching image {img_url}: {e}")
                    progress_bar.update(1)

                if row_images:
                    images.append(row_images)
                else:
                    break

        if not images:
            logging.warning("No images were downloaded.")
            return

        # 获取每个小图的尺寸（假设所有小图尺寸相同）
        tile_width, tile_height = images[0][0].size

        # 计算大图的尺寸
        stitched_width = tile_width * max_cols
        stitched_height = tile_height * max_rows

        # 创建大图并将小图拼接上去
        stitched_image = Image.new('RGB', (stitched_width, stitched_height))
        with tqdm(total=max_rows * max_cols, desc='Stitching images', unit='image') as progress_bar:
            for row in range(len(images)):
                for col in range(len(images[row])):
                    stitched_image.paste(images[row][col], (col * tile_width, row * tile_height))
                    logging.info(f"Added image {col}_{row}.png to stitched image")
                    progress_bar.update(1)

        # 保存大图
        stitched_image_path = os.path.join(save_directory, stitched_image_name)
        stitched_image.save(stitched_image_path)
        logging.info(f"Stitched image saved as {stitched_image_path}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

# 示例使用
base_url = input("Enter base URL for images: ").strip()  # 用户输入 base_url
image_pattern = '{col}_{row}.png'  # 假设小图的命名模式为 col_row.png
max_rows = 10  # 设置尝试的最大行数
max_cols = 10  # 设置尝试的最大列数

download_and_stitch_images(base_url, image_pattern, max_rows, max_cols)

