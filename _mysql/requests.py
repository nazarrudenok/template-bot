import pymysql
from io import BytesIO
from PIL import Image
import os
import requests
from bs4 import BeautifulSoup

def get_photo() -> str:
    try:
        connection = pymysql.connect(
            host='sql8.freemysqlhosting.net',
            user='sql8641333',
            password='SrRcPImvQT',
            database='sql8641333',
            port=3306
        )
        cursor = connection.cursor()

        cursor.execute('SELECT img FROM test')
        image_data = cursor.fetchall()

        save_directory = 'from-db-images/'
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        for i in range(len(image_data)):
            image_stream = BytesIO(image_data[i][0])

            image = Image.open(image_stream)

            image.save(os.path.join(save_directory, f'{i + 1}.jpg'))

        connection.close()
    except Exception as ex:
        return ex
    

def get_data():
    try:
        connection = pymysql.connect(
            host='sql8.freemysqlhosting.net',
            user='sql8641333',
            password='SrRcPImvQT',
            database='sql8641333',
            port=3306
        )
        cursor = connection.cursor()

        cursor.execute('SELECT id, description, price FROM test')
        description = cursor.fetchall()

        return description
    except Exception as ex:
        return ex

    
def count_photos() -> int:
    directory = 'from-db-images/'

    if os.path.exists(directory):
        file_list = os.listdir(directory)
        image_count = len([file for file in file_list if file.endswith('.jpg')])
        return image_count
    else:
        return 0

def get_date():
    url_time = 'https://meteogram.org/time-now/ukraine/lviv/'
    response = requests.get(url_time)
    bs = BeautifulSoup(response.text, 'html.parser')
    time1 = bs.find('span', id='hours').text
    time2 = bs.find('span', id='min1').text
    return f'{time1}:{time2}'