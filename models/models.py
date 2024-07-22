import requests
from utils.methods import cloud_info, upload_file, delete_file


class Connector:
    def __init__(self, token, cloud_path, local_path):
        """
        :param token: Токен доступа к диску
        :param cloud_path: Путь до диска в облаке
        :param local_path: Локальный путь до отслеживаемой папки
        """
        self.local_path = local_path
        self.header = {"Authorization": f"OAuth {token}"}
        self.cloud_path = cloud_path

    def get_info(self) -> list:
        """
        Метод возвращает запрашивает json файл с данными об облачном хранилище ()
        :return: cloud_info(js) функция возвращает список имен файлов в облаке
        """
        path = self.cloud_path.split("/")
        js = requests.get(
            f"https://cloud-api.yandex.net/v1/disk/resources?path={path[0][:-1]}%3A%2F{path[1]}",
            headers=self.header,
        ).json()
        return cloud_info(js)

    def load(self, name: str) -> None:
        """
        :param name: имя файла из локальной директории,
         который нужно загрузить в облако.
        :return: None
        """
        upload_file(
            loadfile=self.local_path + "/" + name,
            savefile=self.cloud_path + "/" + name,
            headers=self.header,
            replace=False,
        )

    def reload(self, name) -> None:
        """
        :param name: имя файла из локальной директории,
         который нужно обновить облакe.
        :return: None
        """
        upload_file(
            loadfile=self.local_path + "/" + name,
            savefile=self.cloud_path + "/" + name,
            headers=self.header,
            replace=True,
        )

    def delete(self, name) -> None:
        """
        :param name: имя файла из локальной директории,
         который нужно обновить облакe.
        :return: None
        """
        delete_file(cloud_dir=self.cloud_path, file_name=name, header=self.header)
