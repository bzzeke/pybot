import requests
import os
import traceback
import requests
import shutil
import tempfile

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from utils import serialize, unserialize

class Cams:

    ALL_CAMERAS = "all"
    cameras = []

    def cams(self, update, context):

        r = requests.get("http://{}/camera_list".format(os.environ["CAMERA_SERVER"]))

        try:
            cameras = r.json()
            keyboard = [
                [InlineKeyboardButton("All", callback_data=self.generate_callback("all"))]
            ]
            for camera in cameras["results"]:
                self.cameras.append(camera["name"])
                keyboard.append([InlineKeyboardButton(camera["name"], callback_data=self.generate_callback(camera["name"]))])

            update.message.reply_text(
                'Select camera:',
                reply_markup=InlineKeyboardMarkup(keyboard))

        except Exception as e:
            print("JSON decode error: {}".format(e))
            traceback.print_exc()


    def get_snapshot(self, update, context):
        query = update.callback_query
        query.answer()
        cam_id = self.get_command(query.data)

        for file in self.download_snapshots(cam_id):
            query.bot.send_photo(chat_id=query.message.chat.id, photo = file)

    def get_video(self, update, context):
        query = update.callback_query
        query.answer()
        meta = self.get_command(query.data)

        file = self.download_video(meta)
        if file != None:
            query.bot.send_video(chat_id=query.message.chat.id, video = file)


    def download_snapshots(self, cam_id):

        files = []

        if cam_id == self.ALL_CAMERAS:
            cam_ids = self.cameras
        else:
            cam_ids = [cam_id]

        for cam_id in cam_ids:
            tfile = tempfile.TemporaryFile()
            url = "http://{}/snapshot/{}".format(os.environ["CAMERA_SERVER"], cam_id)
            with requests.get(url, stream=True) as r:
                shutil.copyfileobj(r.raw, tfile)
                tfile.seek(0)

            files.append(tfile)

        return files


    def download_video(self, meta):

        camera, timestamp = meta.split("_")
        video_file = tempfile.TemporaryFile()
        url = "http://{}/video/{}/{}".format(os.environ["CAMERA_SERVER"], camera, timestamp)

        with requests.get(url, stream=True) as r:
            shutil.copyfileobj(r.raw, video_file)
            video_file.seek(0)

        return video_file if os.fstat(video_file.fileno()).st_size > 0 else None

    def generate_callback(self, payload):

        return serialize(
            "cams",
            "get_snapshot",
            payload
        )

    def get_command(self, payload):
        command, state, data = unserialize(payload)
        return data
