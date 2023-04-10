import requests
import json
from pprint import pprint
from tqdm import tqdm
import datetime
import configparser

config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг

def time_convert(time_vk):    # Функция преобразует дату загрузки фото в привычный формат
    time_bc = datetime.datetime.fromtimestamp(time_vk)
    str_time = time_bc.strftime('%Y-%m-%d time %H-%M-%S')
    return str_time
class foto_VK_request:    # создаем класс
    url_VK = 'http://api.vk.com/method/'
    # url_YD = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    def __init__(self, user_id, version = '5.131'): # функция инициализации атрибутов класса для экземпляра класса
        self.token = config["VK_to_YD"]["VK_token"]
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.json, self.fotos_dict = self.search_fotos()  #инициализация списка фото и списка url для дальнейшей загрузки файла и фоток
        
    def search_fotos(self): # функция поиска фотографий по параметрам (из профиля, с размерами, до пяти штук)
        url = 'https://api.vk.com/method/photos.get'       
        response = requests.get(url, params = {**self.params, 'album_id': 'profile', 'extended' : 1, 'photo_sizes' : 1, 'rev' : 1, 'count' : 5})
        req = response.json()
        albums = req['response']['items']   # список словарей - данные по каждой фотографии (разных размеров)
        fotos_list = [] # список словарей-названий фото с указанием размера по заданию
        fotos = {}  # словарь названий фото с указанием размера
        # fotos_url_list = []
        for album in albums: # перебор списка словарей - каждую фото со всеми вариантами размеров
            for sizes in album['sizes']: # перебор каждого варианта размеров одного фото
                if sizes['type'] == 'z':    # выбор максимального размера фото
                    new_name_foto = album['likes']['count'] # название фото по числу лайков
                    if str(new_name_foto) + '.jpg' not in fotos.keys(): # условие проверки одинакового количества лайков в названии фото
                        fotos[str(new_name_foto) + '.jpg'] = sizes['url']  # присвоение имени фото по количеству лайков
                        fotos_list.append({'file_name' : str(new_name_foto) + '.jpg'}) # добавление в список, который потом запишем в отдельный файл по заданию
                    else:   # условие при одинаковом колиестве лайков
                        time_warp = time_convert(album['date']) # конвертация времени в удобный формат
                        fotos[str(new_name_foto) + time_warp + '.jpg'] = sizes['url']  # присвоение имени фото по количеству лайков и времени
                        fotos_list.append({'file_name' : str(new_name_foto) + time_warp + '.jpg'}) # добавление в список, который потом запишем в отдельный файл по заданию

        # pprint(req)
        # pprint(albums)
        # pprint(fotos)
        # pprint(fotos_list)
        # pprint(fotos_url_list)
        return fotos_list, fotos
    
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

    def upload_file_to_disk(self, VK_fotos_dict):   #функция загружает файл в созданную ранее папку
        yandex_upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload/'    #url в соответствии с нужным методом (на Полигоне Яндекса)
        headers = self.get_headers()    # назначаем определенные ранее заголовки
        
        for foto_name, i in zip(VK_fotos_dict.keys(), tqdm(range(len(VK_fotos_dict)))):       # перебираем отобранные по размеру фото в словаре и делаем прогресс-бар
            params_upload = {'path': f'PYTHON2/{foto_name}', 'url': VK_fotos_dict[foto_name]}  # обозначаем папку на ЯДиске, новое название файла, ссылку на отобранное фото в ВК (из словаря)
            response = requests.post(url=yandex_upload_url, params=params_upload, headers=headers) # делаю запрос на загрузку файла
            # print(response.content)
            if response.status_code == 201: # проверка
                print("Success")
            else:
                pprint(response.status_code)

if __name__== '__main__':   # запуск кода
    YD_foto = foto_VK_request(config["VK_to_YD"]["VK_id"])  # создание экземпляра класса
    New_foto = fotos_to_YD(config["VK_to_YD"]["YD_token"])  # создание экземпляра класса    
    folder = New_foto.get_upload_dir()  # вызов метода для создания папки
    res = New_foto.upload_file_to_disk(YD_foto.fotos_dict)    # вызов метода, загружающего файлы в папку на Ядиске
    
    with open('fotos_data.json', 'w') as outfile:    # запись списка названий и размеров отобранных фото в файл
        json.dump(YD_foto.json, outfile)
