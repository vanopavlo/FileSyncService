import os
import time

from dotenv import load_dotenv, find_dotenv, dotenv_values
import logging
from utils.methods import *
from models.models import Connector

# Происходит проверка наличия файла .env, в случае отсутствия выводитяся ошибка,
# иначе же применятеся dotenv_values и загружаетсяв переменную env
# для дальнейшего использования (в формате словаря)

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    env = dotenv_values()
# Создается переменная headers, которая используется для простого доступа к диску
headers = {"Authorization": f"OAuth {env['TOKEN']}"}

# Настраивается класс коннектор в него передаются необходимые значения из переменной env:
# Токен, Путь до файла в облаке, Путь до файла локально
connect = Connector(
    token=env["TOKEN"], cloud_path=env["CLOUD_PATH"], local_path=env["LOCAL_PATH"]
)

# Конфигурируется логгер
logger = logging.getLogger("file_logs")
logging.basicConfig(
    level=logging.INFO,
    filename="log.txt",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


if __name__ == "__main__":
    # При запуске в переменную start_mod_time записывается словарь
    # {время изменения файла: имя файла}
    start_mod_time = local_check_time(env["LOCAL_PATH"])
    logger.info("\nЗапуск программы...")
    while True:
        # В переменную cloud_files записываются названия файлов из облака
        cloud_files = connect.get_info()
        # В переменную local_files записываются названия файлов в облаке
        local_files = local_get_info(env["LOCAL_PATH"])

        # Если кол-во файлов в облаке и на диске не равны между собой,
        # программа пробует загрузить или удалить файлы
        if cloud_files != local_files:
            try:
                # Если файлов больше лоакльно, то программа загружает их
                if len(local_files) > len(cloud_files):
                    # В список load_list попадают файлы, которые есть локально, но нет на диске
                    load_list = [
                        i_file for i_file in local_files if i_file not in cloud_files
                    ]
                    for i_load_file in load_list:
                        # Метод connect.load загружает файлы на диск
                        connect.load(name=i_load_file)
                        logger.info(f"На диск был загружен файл: {i_load_file}")

            # При возникновении ошибок программа записывает лог в файл логов, но не прекращает работу
            except Exception as ex:
                logger.error(ex)

            # Блок запускается при равном колличесве файлов между локальной и облачной директорией
            else:
                try:
                    # Создается список с лишними файлами в облаке
                    delete_list = [
                        i_del_file
                        for i_del_file in cloud_files
                        if i_del_file not in local_files
                    ]
                    for i_del_file in delete_list:
                        # Файлы из списка delete_list удаляются при помощи метода connect.delete
                        connect.delete(i_del_file)
                        logger.info(f"С диска был удален файл: {i_del_file}")
                except Exception as ex:
                    logger.error(ex)
        # Если файлов в лоакльной и удаленной директории равное количество запускается блок else
        else:
            try:
                # В пременную time_mod записываетсся словарь
                # {Время изменения файла: имя файла}
                time_mod = local_check_time(env["LOCAL_PATH"])

                # Если файл изменялся с момента начала прогаммы выполняется блок if
                if (
                    start_mod_time != time_mod
                ):  # or len(start_mod_time) == len(time_mod):
                    # Файлы которые модифицировались записываются в переменную mod_files
                    mod_files = start_mod_time.keys() - time_mod.keys()
                    for i_time in mod_files:
                        # Файлы из списка обновляются на диске, с помощью метода connect.reload
                        connect.reload(start_mod_time[i_time])
                        logger.info(
                            f"На диске был обновлен файл: {start_mod_time[i_time]}"
                        )
                    # После обновления файлов на диске start_mod_time перезаписыватся
                    start_mod_time = local_check_time(env["LOCAL_PATH"])
            except Exception as ex:
                logger.error(ex)
        # В time.sleep() передается кол-во секунд периода активности прграмыы из переменной env
        time.sleep(int(env["SYNC_PER"]))
