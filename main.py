import os
import time

from mqtt import Mqtt

from commands.temp import Temp
from commands.cams import Cams
from commands.cry import Cry
from commands.set import Set
from api import ApiServer
from mail import MailServer
from tg import Telegram

from utils import import_env, log

if __name__ == "__main__":
    import_env()

    mqtt = Mqtt()
    telegram = Telegram()
    telegram.start()

    temp_command = Temp(telegram = telegram, mqtt = mqtt)
    cams_command = Cams(telegram = telegram)
    cry_command = Cry(telegram = telegram, mqtt = mqtt)
    set_command = Set(telegram = telegram, mqtt = mqtt)

    api_server = ApiServer(telegram = telegram)
    api_server.start()

    mail_server = MailServer()
    mail_server.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        log("[main] Stopping all")
        telegram.stop = True
        mail_server.stop()
        api_server.stop()

        telegram.join()
        mail_server.join()
        api_server.join()



