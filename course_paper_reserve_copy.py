import requests
import json
from pprint import pprint

import configparser  # импортируем библиотеку

config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг

class foto_VK_request:    # создаем класс
    url_VK = 'http://api.vk.com/method/'
    url_YD = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    def __init__(self, user_id, version = '5.131'): # функция инициализации атрибутов класса для экземпляра класса
        self.token = config["VK_to_YD"]["VK_token"]
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.json, self.url_list = self.search_fotos()  #инициализация списка фото и списка url для дальнейшей загрузки файла и фоток
    
    def search_fotos(self): # функция поиска фотографий по параметрам (из профиля, с размерами, до пяти штук)
        url = 'https://api.vk.com/method/photos.get'       
        response = requests.get(url, params = {**self.params, 'album_id': 'profile', 'extended' : 1, 'photo_sizes' : 1, 'count' : 5})
        req = response.json()
        albums = req['response']['items']   # список словарей - данные по каждой фотографии (разных размеров)
       
        fotos_list = [] # список словарей-названий фото с указанием размера по заданию
        fotos = {}  # словарь названий фото с указанием размера
        fotos_url_list = []
        for album in albums: # перебор списка словарей - каждую фото со всеми вариантами размеров
            for sizes in album['sizes']: # перебор каждого варианта размеров одного фото
                if sizes['type'] == 'z':    # выбор максимального размера фото
                    fotos['file_name'] = str(album['likes']['count']) + '.jpg'  # присвоение имени фото по заданию
                    fotos['size'] = 'z' # присвоение размера фото по заданию
                    fotos_list.append(fotos) # добавление в список, который потом запишем в отдельный файл по заданию
                    fotos_url_list.append(sizes['url'])

        # pprint(req)          
        # pprint(fotos_list)
        # pprint(fotos_url_list)
        return fotos_list, fotos_url_list
    
class fotos_to_YD:    # создаем класс
    def __init__(self, token_YD):   # функция инициализации атрибутов класса для экземпляра класса
        self.token = token_YD

    def get_headers(self):  # функция определяет что нам вернет Яндекс и передает токен, чтоб Яндекс понял, что я это я
        return {
            'Content-Type': 'application/json', # передать тип - в виде словаря
            'Authorization': 'OAuth {}'.format(self.token)  # авторизационный заголовок
        }

    def get_upload_dir(self): #функция создает на ЯДиске папку, куда буду размещать файл
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/"    #url в соответствии с нужным методом (на Полигоне Яндекса)
        headers = self.get_headers()    # назначаем определенные ранее заголовки
        params = {'path': 'PYTHON2'}    #путь, куда грузить файл (название папки)
        return requests.put(url = upload_url, headers = headers, params = params)   #создание папки, куда будем грузить файл

    def upload_file_to_disk(self, VK_fotos_url_list):   #функция заружает файл в созданную ранее папку
        yandex_upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload/'    #url в соответствии с нужным методом (на Полигоне Яндекса)
        headers = self.get_headers()    # назначаем определенные ранее заголовки
        folder = self.get_upload_dir()  # вызов метода для создания папки
        for foto_url in VK_fotos_url_list:       # перебираем URL отобранных по размеру фото  
            params_upload = {'path': 'PYTHON2/new.jpg', 'url': foto_url}  # обозначаем папку на ЯДиске, новое название файла. Во втором аргументе - ссылку на отобранное фото в ВК
            response = requests.post(url=yandex_upload_url, params=params_upload, headers=headers) # делаю запрос на загрузку файла
            
            print(response.content)
            if response.status_code == 201: # проверка
                print("Success")
            else:
                print(response.status_code)

if __name__== '__main__':   # запуск кода
    YD_foto = foto_VK_request(config["VK_to_YD"]["VK_id"])  # создание экземпляра класса
    New_foto = fotos_to_YD(config["VK_to_YD"]["YD_token"])  # создание экземпляра класса    
    res = New_foto.upload_file_to_disk(YD_foto.url_list)    # вызов метода, загружающего файлы в папку на Ядиске
   
    with open('fotos_data.json', 'w') as outfile:    # запись списка названий и размеров отобранных фото в файл
        json.dump(YD_foto.json, outfile)
