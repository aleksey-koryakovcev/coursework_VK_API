"""Резервное копирование фотографий профиля
Вконтакте на Яндекс.Диск"""

import os
import requests
import settings

access_token = os.getenv('ACCESSTOKEN')
yandex_token = os.getenv('YANDEXTOKEN')
user_id = os.getenv('USERID')

class VKPhoto:
    """Описание класса фото ВК"""
    def __init__(self, access_token, user_id, version='5.199'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def get_photos(self):
        """Сохраняет фото с профиля ВК"""
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id,
                  'album_id': 'profile',
                  'photo_sizes': 1,
                  'extended': 1,
                  'rev': 0}
        response = requests.get(url, params={**self.params, **params}, timeout=3).json()
        response_ = response['response']['items']
        list_photos = []
        for item in response_:
            list_photos.append(item['sizes'][-1]['url'])
            list = list_photos[0]
            print(list)
            name_photo = 'photo.jpg'
            download = requests.get(list, timeout=3)
            with open(name_photo, 'wb') as file:
                file.write(download.content)
        return response

class YandexPhoto:
    """Описание класса сохранения фото на Яндекс.Диск"""
    def __init__(self, yandex_token, name_folder):
        self.token = yandex_token
        self.params = {'yandex_token': self.token}
        self.headers = {'Authorization': self.token}
        self.folder = self.create_folder(name_folder)

    def create_folder(self, name_folder):
        """Создает папку для сохранения фото на Яндекс.Диск"""
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': name_folder}
        if requests.get(url, headers=self.headers, params=params, timeout=3).status_code != 200:
            requests.put(url, headers=self.headers, params=params, timeout=3)
            print(f'Папка {name_folder} создана в каталоге Яндекс.Диска')
        return name_folder

    def get_headers(self):
        """Параметры заголовков"""
        params = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }
        return params

    def get_download_link(self, file_path):
        """Сохраняет ссылки фотографий"""
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': file_path, 'overwrite': 'true'}
        response = requests.get(url, headers=headers, params=params, timeout=3)
        return response.json()

    def download_photo(self, file_path, name_photo):
        """Загружает фотографии в папку на Яндекс.Диск"""
        href_json = self.get_download_link(file_path=file_path)
        href = href_json['href']
        response = requests.put(href, data=open(name_photo, 'rb'), timeout=3)
        response.raise_for_status()
        if response.status_code == 201:
            print('Фото загружено')


if __name__ == '__main__':
    vk = VKPhoto(access_token, user_id)
    vk.get_photos()
    yandex = YandexPhoto(yandex_token, 'VK photo')
    yandex.download_photo('VK photo/photo', 'photo.jpg')
