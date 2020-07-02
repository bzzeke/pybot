import logging
from mqtt import Mqtt
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, Filters
import os

from commands.temp import Temp
from commands.cams import Cams
from commands.cry import Cry
from commands.set import Set

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

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("temp", temp_command.run))

    dp.add_handler(CommandHandler("cams", cams_command.cams))
    dp.add_handler(CallbackQueryHandler(cams_command.get_video, pattern="^cams,get_video\:.*$"))
    dp.add_handler(CallbackQueryHandler(cams_command.get_snapshot, pattern="^cams,get_snapshot\:.*$"))

    dp.add_handler(CommandHandler("cry", cry_command.ask))
    dp.add_handler(CallbackQueryHandler(cry_command.enable, pattern="^cry,enable\:.*$"))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('set', set_command.select_topic)],

        states={
            "publish": [MessageHandler(Filters.all, set_command.publish)],
        },
        fallbacks = []
    ))
    dp.add_handler(CallbackQueryHandler(set_command.set_value, pattern="^set,topic\:.*$"))
    dp.add_handler(CallbackQueryHandler(set_command.publish, pattern="^set,value\:.*$"))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
