from typing import Optional, Type, List, Any
import json
import requests
import os


def cloud_info(json_file: json) -> list:
    """
    :param json_file: json файл с информацией о файлах на диске
    :return: answer: list Имена файлов
    """
    items = json_file["_embedded"]["items"]
    answer = list()
    for i_file in items:
        for i_key, i_val in i_file.items():

            if i_key == "name":
                answer.append(i_val)
    return answer


def upload_file(loadfile, savefile, headers, replace=False):
    """Функция при загружает или/и обновляет (replace=False/True) файлы на диске.
    savefile: Путь к файлу на Диске
    loadfile: Путь к загружаемому файлу
    replace: true or false Замена файла на Диске"""
    res = requests.get(
        f"https://cloud-api.yandex.net/v1/disk/resources/upload?path={savefile}&overwrite={replace}",
        headers=headers,
    ).json()
    print(loadfile)
    with open(loadfile, "rb") as f:
        try:
            requests.put(res["href"], files={"file": f})
        except KeyError:
            print(res)


def delete_file(cloud_dir, file_name, header):
    """Функция удаляет файлы на диске
    dir: Директория на диске
    file_name: имя файлы
    header: "Authorization": "OAuth env['токен доступа']"""
    requests.delete(
        f"https://cloud-api.yandex.net/v1/disk/resources?path={cloud_dir}/{file_name}",
        headers=header,
    )


def local_get_info(local_dir):
    """Функция принимает путь до локальной директории и
    возвращает список файлов в ней в формате списка.
    dir: Локальная директория"""
    test = os.walk(local_dir)
    (
        path,
        dirs,
        files,
    ) = next(test)
    for i_file in files:
        if str(i_file).startswith("~$"):
            files.remove(str(i_file))
    return sorted(files)[1:]


def local_check_time(path):
    """ "Функция принимает пуять до локальной директории и
    возвращает словарь {время изменения: название файла}
    path: путь до локальной директории"""
    files = local_get_info(path)
    time = []
    for i_file in sorted(files):
        time.append(os.path.getctime(path + "/" + i_file))
    return dict(zip(time, files))
