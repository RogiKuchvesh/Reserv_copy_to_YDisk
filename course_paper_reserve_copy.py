import json
import configparser
from foto_VK_request import FotoVKrequest
from fotos_to_YD import FotosYD

config = configparser.ConfigParser()
config.read("settings.ini")

if __name__ == "__main__":

    vk_id = input('Введите ID пользователя: ')
    vk_token = config["VK_to_YD"]["VK_token"]    
    count_photos = input('Введите количество фотографий: ')
    yd_token = config["VK_to_YD"]["YD_token"]

    YD_foto = FotoVKrequest(vk_id, vk_token, count_photos)
    New_foto = FotosYD(yd_token)
    folder = New_foto.get_upload_dir()
    res = New_foto.upload_file_to_disk(YD_foto.fotos_dict)

    with open("fotos_data.json", "w") as outfile:
        json.dump(YD_foto.json, outfile)
