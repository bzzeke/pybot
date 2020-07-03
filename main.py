import os
import time

from mqtt import Mqtt
from telegram.ext import Updater

from commands.temp import Temp
from commands.cams import Cams
from commands.cry import Cry
from commands.set import Set
from api import ApiServer
from mail import MailServer
from utils import import_env, log

if __name__ == "__main__":
    import_env()

    updater = Updater(os.environ["BOT_TOKEN"], use_context=True)

    bot = updater.bot
    dispatcher = updater.dispatcher


    mqtt = Mqtt()
    temp_command = Temp(dispatcher = dispatcher, mqtt = mqtt)
    cams_command = Cams(dispatcher = dispatcher)
    cry_command = Cry(dispatcher = dispatcher, mqtt = mqtt)
    set_command = Set(dispatcher = dispatcher, mqtt = mqtt)

    api_server = ApiServer(bot=bot, dispatcher=dispatcher)
    api_server.start()

    mail_server = MailServer()
    mail_server.start()

    updater.start_polling()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        log("[main] Stopping all")
        updater.stop()

        mail_server.stop()
        api_server.stop()

        mail_server.join()
        api_server.join()



