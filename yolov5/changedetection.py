import os
import cv2
import pathlib
import requests
from datetime import datetime

class ChangeDetection:
    result_prev = []
    HOST = "https://jylim.pythonanywhere.com"
    username = "admin"
    password = "superuser"
    token = ""
    title = ""
    text = ""

    def __init__(self):
        self.result_prev = []

        res = requests.post(self.HOST + "/api-token-auth/", {
            "username": self.username,
            "password": self.password,
        })
        res.raise_for_status()
        self.token = res.json()["token"]
        print(self.token)

    def add(self, detected_current, save_dir, image):
        self.title = ""
        self.text = ""
        change_flag = 0
        i = 0
        while i < len(self.result_prev):
            if self.result_prev[i] not in detected_current:
                change_flag = 1
                self.title = str(self.result_prev[i])
                self.text = str(self.result_prev[i]) + ","
            i += 1
        i = 0
        while i < len(detected_current):
            if detected_current[i] not in self.result_prev:
                change_flag = 1
                self.title = str(detected_current[i])
                self.text = str(detected_current[i]) + ","
            i += 1

        self.result_prev = detected_current[:]

        if change_flag == 1:
            self.send(save_dir, image)

    def send(self, save_dir, image):
        now = datetime.now()
        now.isoformat()

        today = datetime.now()
        save_path = os.getcwd() / save_dir / "detected" / str(today.year) / str(today.month) / str(today.day)
        pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

        full_path = save_path / "{0}-{1}-{2}-{3}.jpg".format(today.hour, today.minute, today.second, today.microsecond)

        dst = cv2.resize(image, dsize=(320, 240), interpolation=cv2.INTER_AREA)
        cv2.imwrite(full_path, dst)

        headers = {"Authorization": "JWT " + self.token, "Accept": "application/json"}

        data = {
            "title": self.title,
            "text": self.text,
            "created_date": now,
            "published_date": now
        }
        file = {"image": open(full_path, "rb")}
        res = requests.post(self.HOST + "/api_root/Post/", data=data, files=file, headers=headers)
        print(res)
        