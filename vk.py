import json
from pprint import pprint
from sqlite3 import DateFromTicks
import requests
from VK_TOKEN import VK_TOKEN as token_VK
from YADISK_TOKEN import TOKEN_YADISK as token_YD
import datetime


class VK: 
  url = 'https://api.vk.com/method/' 
  def __init__(self, tkn, version): 
      self.params = { 
          'access_token': tkn, 
          'v': version 
      }

# Основые функции
  # Информация о пользователе   
  def users_get_info(self, user_ids):
    url_for_func = self.url + 'users.get' 
    info_params = { 
        'user_ids': user_ids, 
        'fields': 'id, education, city' 
    } 
    response = requests.get(url_for_func, params={**self.params, **info_params}).json()  
    return response['response'] 
     
  # ID пользователя в цифрах   
  def users_get_id(self, user_ids):
    url_for_func = self.url + 'users.get' 
    info_params = { 
        'user_ids': user_ids, 
        'fields': 'id' 
    } 
    response = requests.get(url_for_func, params={**self.params, **info_params}).json() 
    return response['response'][0]['id']

  # Собирает два словаря. 
  # Первый Ключ - URL на фото, Значение - количество лайков у фотографии
  # Второй собирает информацию о фото и записывает в файл inf.json
  def get_photos_url_and_like_in_dict(self,owner_id):
    url_for_func = self.url + 'photos.get'
    owner_id_for_params = self.users_get_id(owner_id)
    url_list_type_z = []
    likes_list = []
    dict_url_and_likes = None
    my_json = []
    params_photoget = {
      'owner_id': owner_id_for_params,
      'album_id': 'profile',
      'extended': 1
    }
    response = requests.get(url_for_func, params={**self.params, **params_photoget}).json()
    for dict_1 in response['response']['items']:
      if dict_1['likes']['count'] in likes_list:
        likes_list.append(str(dict_1['likes']['count']) + ' - ' +
          (DateFromTicks(dict_1['date'])).strftime('%d-%m-%Y'))
      else:
        likes_list.append(dict_1['likes']['count'])
    for dict_2 in response['response']['items']:
      max_size = 0
      dict_format = {
        's': 1,
        'm': 2,
        'x': 3,
        'o': 4,
        'p': 5,
        'q': 6,
        'r': 7,
        'y': 8,
        'z': 9,
        'w': 10,
        }
      best_url = None
      for size in dict_2['sizes']:
        if dict_format[size['type']] > max_size:
          best_url = size['url']
          max_size = dict_format[size['type']]
      url_list_type_z.append(best_url)
    dict_url_and_likes = dict(zip(url_list_type_z, likes_list))
    for url,like in dict_url_and_likes.items():
      for inf in response['response']['items']:
        for size in inf['sizes']:
          if url == size['url']:
            my_dict = {'file_name':str(like) + '.jpg', 'size': size['type']} 
            my_json.append(my_dict)
    with open('inf.json', 'a', encoding= 'utf-8') as f:
      json.dump(my_json, f)
    return dict_url_and_likes

# Дополнительные функции(что-то пробовал)
  # Функция для загрузки всех фото с страницы. Собирает строки для метода getByld
  # Формат string(iduser_idphoto)
  def get_user_and_photos_id_for_all_photo(self, owner_ids): 
    users_photos = {}
    list_with_id_photos = []
    list_string_for_getByld = [] 
    url_for_func = self.url + 'photos.getAll' 
    owner_ids = self.users_get_id(owner_ids) 
    get_photos_params = { 
        'owner_id': owner_ids, 
      } 
    response = requests.get(url_for_func, params={**self.params, **get_photos_params}).json() 
    list_with_ids =response['response']['items'] 
    for x in list_with_ids: 
      id_user = x['owner_id'] 
      id_photo = x['id']
      list_with_id_photos.append(id_photo) 
      users_photos[id_user]= list_with_id_photos  
    for k,v in users_photos.items():
      for values in v: 
        list_string_for_getByld.append(str(k) + '_' + str(values))
    return list_string_for_getByld 
  
  # Функция возвращает список фотоальбомов пользователя
  def photos_getAlbums_inf(self, owner_id): 
    url_for_func = self.url + 'photos.getAlbums' 
    owner_id = self.users_get_id(owner_id) 
    get_photos_albums_params = { 
      'owner_id': owner_id, 
      'photo_size': 1 
    }  
    response = requests.get(url_for_func, params={**self.params, **get_photos_albums_params}).json() 
    return response 

  # Функция для второго способа получать аватарки  Собирает строки для метода getByld
  # Формат string(iduser_idphoto)
  def get_iduser_idavatars(self, owner_id):
    user_photos_from_ava = {}
    list_for_dict_with_ids_photo = []
    list_string_for_getByld = [] 
    url_for_func = self.url + 'photos.get'
    owner_id = self.users_get_id(owner_id)
    get_inf_ava_params = {
      'owner_id': owner_id,
      'album_id': 'profile',
      'extended': 1,
      'rev': 0
    }
    response = requests.get(url_for_func, params={**self.params, **get_inf_ava_params}).json()
    list_with_ids =response['response']['items']
    for x in list_with_ids: 
      id_user = x['owner_id'] 
      id_photo = x['id']
      list_for_dict_with_ids_photo.append(id_photo) 
      user_photos_from_ava[id_user]= list_for_dict_with_ids_photo 
    for k,v in user_photos_from_ava.items():
      for values in v: 
        list_string_for_getByld.append(str(k) + '_' + str(values))
    return list_string_for_getByld
  
  # Функция собирает URL фото аватарки 
  def get_url_for_ava_in_list(self,owner_id):
    url_list = []
    url_for_func = self.url + 'photos.getById'
    list_str_for_method = self.get_iduser_idavatars(owner_id)
    string_with_iduser_idsphotos = ''
    for iduser_idphoto in list_str_for_method:
      string_with_iduser_idsphotos += ',' + iduser_idphoto
    
    params_for_get_url_avatars = {
      'photos': string_with_iduser_idsphotos[1:],
      'extended': 1
    }
    response = requests.get(url_for_func, params={**self.params, **params_for_get_url_avatars}).json()
    for x in response['response']:
      url_list.append(x['orig_photo']['url'])
    return url_list 
 

class YandexDisk:
  url = 'https://cloud-api.yandex.net' 
  def __init__(self, token):
    self.token = token

# Основные функции
  # Генерирует headers для запросов на ЯндексДиск
  def get_headers(self):
    return {
      'Content-Type': 'application/json',
      'Authorization': f'OAuth {self.token}'
    }

  # Информация о диске
  def get_files_list(self):
      url_for_inf_about_disk = self.url + '/v1/disk/resources/files'
      headers = self.get_headers()
      response = requests.get(url_for_inf_about_disk, headers=headers)
      return response.json()
  
  # Создает новую папку
  def new_folder(self, path):
    url_for_new_folder = self.url + '/v1/disk/resources'
    headers = self.get_headers()
    requests.put(f'{url_for_new_folder}?path={path}', headers=headers)

  # Получает ссылку на место в ЯндексДиске для загрузки
  def get_upload_link(self, disk_file_path):
    url_for_link = self.url + '/v1/disk/resources/upload'
    headers = self.get_headers
    params =  {'path': disk_file_path, 'overwrite': 'true'}
    response =  requests.get(url_for_link, headers=headers, params=params)
    return response.json()

  # Загружает файлы по URL на ЯндексДиск
  def post_on_disk_from_internet(self, url_file, file_name):
    url_for_func = self.url + '/v1/disk/resources/upload'
    headers = self.get_headers()
    params_for_func = {'url': url_file, 'path': file_name}
    response = requests.post(url_for_func, headers=headers, params=params_for_func)


def main_func():
  while True:
    command = input('''
    q - команда, которая закроет программу
    d - команда для загрузки аватарок пользователя ВК на ЯндексДиск (Обязательные параметры: TokenVK, id пользователя, TokenYandexDisk)
        СОЗДАЙТЕ ПАПКУ ДЛЯ СКАЧИВАНИЯ ФАЙЛОВ!!!(Папка должна находиться в корне диска)
    i - команда для получчения информации о пользователе (Обязательные параметры: TokenVK, id пользователя)
    c - команда создает новую папку в корне диска(Обязательные параметры: имя папки, TokenYandexDisk ) 
    ''')
    if command == 'q':
      print('Вы закрыли программу')
      break
    if command == 'd':
      try:
        name_folder = input('Введите имя папки: ')
        user_id = input('Введите id пользователя: ')
        tkn_vk = input('Введите TokenVK: ')
        client_1_VK = VK(tkn_vk, '5.131')
        url_likes_dict = client_1_VK.get_photos_url_and_like_in_dict(user_id)
        tkn_yd = input('Введите TokenYD: ')
        client_1_YD = YandexDisk(tkn_yd)
        for k, v in url_likes_dict.items():
          client_1_YD.post_on_disk_from_internet(k, f'disk:/{name_folder}/{v}')
      except:
        print('Данные введены некорректно или у пользователя не установлена аватарка')
    elif command == 'i':
      try:
        user_id = input('Введите id пользователя: ')
        tkn_vk = input('Введите TokenVK: ')
        client_1_VK = VK(tkn_vk, '5.131')
        pprint(client_1_VK.users_get_info(user_id))
      except:
        print('Данные введены некорректно')
    elif command == 'c':
      try:
        tkn_yd = input('Введите TokenYD: ')
        folder_name = input('Введите имя новой папки на диске: ')
        client_1_YD = YandexDisk(tkn_yd)
        client_1_YD.new_folder(folder_name)
      except:
        print('Ошибка!')


main_func()
