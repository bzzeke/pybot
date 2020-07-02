import logging
from mqtt import Mqtt
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, Filters
import os

from commands.temp import Temp
from commands.cams import Cams
from commands.cry import Cry
from commands.set import Set
from api import ApiServer

from utils import import_env

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    import_env()

    mqtt = Mqtt()
    temp_command = Temp(mqtt = mqtt)
    cams_command = Cams()
    cry_command = Cry(mqtt = mqtt)
    set_command = Set(mqtt = mqtt)

    updater = Updater(os.environ["TOKEN"], use_context=True)

    bot = updater.bot
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("temp", temp_command.run))

    dispatcher.add_handler(CommandHandler("cams", cams_command.cams))
    dispatcher.add_handler(CallbackQueryHandler(cams_command.get_video, pattern="^cams,get_video\:.*$"))
    dispatcher.add_handler(CallbackQueryHandler(cams_command.get_snapshot, pattern="^cams,get_snapshot\:.*$"))

    dispatcher.add_handler(CommandHandler("cry", cry_command.ask))
    dispatcher.add_handler(CallbackQueryHandler(cry_command.enable, pattern="^cry,enable\:.*$"))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('set', set_command.select_topic)],

        states={
            "publish": [MessageHandler(Filters.all, set_command.publish)],
        },
        fallbacks = []
    ))
    dispatcher.add_handler(CallbackQueryHandler(set_command.set_value, pattern="^set,topic\:.*$"))
    dispatcher.add_handler(CallbackQueryHandler(set_command.publish, pattern="^set,value\:.*$"))

    api_server = ApiServer(bot=bot, dispatcher=dispatcher)
    api_server.start()

    updater.start_polling()
    updater.idle()




if __name__ == "__main__":
    main()
