import requests
from pprint import pprint
from tqdm import tqdm

class FotosYD:
    def __init__(self, token_YD):
        self.token = token_YD

    def get_headers(self):
        return {
            "Content-Type": "application/json", 
            "Authorization": "OAuth {}".format(self.token),
        }

    def get_upload_dir(self):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/"
        headers = self.get_headers()
        params = {"path": "PYTHON2"}
        return requests.put(url=upload_url, headers=headers, params=params)

    def upload_file_to_disk(self, VK_fotos_dict):
        yandex_upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload/"
        headers = self.get_headers()

        for foto_name, i in zip(VK_fotos_dict.keys(), tqdm(range(len(VK_fotos_dict)))):
            params_upload = {
                "path": f"PYTHON2/{foto_name}",
                "url": VK_fotos_dict[foto_name],
            }
            response = requests.post(url=yandex_upload_url, params=params_upload, headers=headers)
            if response.status_code == 201:
                print("Success")
            else:
                pprint(response.status_code)