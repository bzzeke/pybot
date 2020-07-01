import logging
from mqtt import Mqtt
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler
import os

from commands.temp import Temp
from commands.cams import Cams
from utils import import_env

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    import_env()

    mqtt = Mqtt()
    temp_command = Temp(mqtt = mqtt)
    cams_command = Cams()

    updater = Updater(os.environ["TOKEN"], use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("temp", temp_command.run))

    dp.add_handler(CommandHandler("cams", cams_command.cams))
    dp.add_handler(CallbackQueryHandler(cams_command.get_video, pattern="^cams,get_video\:.*$"))
    dp.add_handler(CallbackQueryHandler(cams_command.get_snapshot, pattern="^cams,get_snapshot\:.*$"))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
