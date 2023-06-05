import requests
from pprint import pprint
import datetime

def time_convert(time_vk):
        time_bc = datetime.datetime.fromtimestamp(time_vk)
        str_time = time_bc.strftime("%Y-%m-%d time %H-%M-%S")
        return str_time

class FotoVKrequest:
    url_VK = "http://api.vk.com/method/"

    # def __init__(self, user_id, token, version="5.131"):
    def __init__(self, user_id, token, count, version="5.131"):
        self.token = token
        self.id = user_id
        self.count = count
        self.version = version
        self.params = {"access_token": self.token, "v": self.version}
        self.json, self.fotos_dict = self.search_fotos()
    
    # def search_fotos(self):
    def search_fotos(self):
        url = "https://api.vk.com/method/photos.get"
        response = requests.get(
            url,
            params={
                **self.params,
                "album_id": "profile",
                "extended": 1,
                "photo_sizes": 1,
                "rev": 1,
                "count": self.count,
            },
        )
        req = response.json()
        pprint(req)
        albums = req["response"]["items"]
        fotos_list = []
        fotos = {}

        for album in albums:
            for sizes in album["sizes"]:
                max_size = 0
                max_photo = None
                if sizes["width"] * sizes["height"] > max_size:
                    max_size = sizes["width"] * sizes["height"]
                    max_photo = sizes["url"]
                    new_name_foto = album["likes"]["count"]
                    if str(new_name_foto) + ".jpg" not in fotos.keys():
                        fotos[str(new_name_foto) + ".jpg"] = max_photo
                        fotos_list.append({"file_name": str(new_name_foto) + ".jpg"})
                    else:
                        time_warp = time_convert(album["date"])
                        fotos[str(new_name_foto) + time_warp + ".jpg"] = sizes["url"]
                        fotos_list.append(
                            {"file_name": str(new_name_foto) + time_warp + ".jpg"}
                        )

        return fotos_list, fotos
