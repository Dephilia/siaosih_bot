#!/usr/bin/env pipenv run python

"""
Nonsense plurk bot

Distributed under terms of the MIT license.
"""

from plurk_oauth import PlurkAPI
from multiprocessing import Process
import typing
import requests
import json
import re
import loguru
import datetime
import time
import random
import schedule
import sqlite3

class Bot:
    def __init__(self, token_file, database):

        self.main_flag = True
        self.offset = 0
        self.database = database

        self.plurk = PlurkAPI.fromfile(token_file)
        user_channel = self.plurk.callAPI("/APP/Realtime/getUserChannel")
        self.comet_server_url = user_channel["comet_server"]
        loguru.logger.info("Start pulling from comet server: " + self.comet_server_url)

        con = sqlite3.connect(self.database)
        cur = con.cursor()
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='users' ''')
        #if the count is 1, then table exists
        if cur.fetchone()[0]==1: 
            loguru.logger.info("Table exists.")
        else:
            #create table
            cur.execute('''CREATE TABLE IF NOT EXISTS users
                         (id real)''')
            loguru.logger.info("Table not exists, create one.")

        con.commit()
        con.close()

    def add_user(self, id):
        if self.if_user(id):
            # If already in
            return False
        con = sqlite3.connect(self.database)
        cur = con.cursor()

        insert_with_param = """INSERT INTO users 
                          (id)
                          VALUES (?);"""

        data_tuple = (id, )
        cur.execute(insert_with_param, data_tuple)

        con.commit()
        con.close()
        return True

    def remove_user(self, id):
        if not self.if_user(id):
            # If not in
            return False
        con = sqlite3.connect(self.database)
        cur = con.cursor()
        cur.execute("DELETE FROM users WHERE id=?;", (id,))

        con.commit()
        con.close()
        return True

    def if_user(self, id):
        result = False
        con = sqlite3.connect(self.database)
        cur = con.cursor()
        cur.execute("SELECT count(id) FROM users WHERE id=?;", (id,))
        if cur.fetchone()[0] >= 1: 
            result = True
        con.close()
        return result

    def is_friend(self, id):
        opt = {
            'user_id': id
        }
        resp = self.plurk.callAPI("/APP/Profile/getPublicProfile", options=opt)
        return resp["are_friends"]

    def gen_msg(self):
        wara_imgs = [
            "https://i.imgur.com/3G7rJ06.jpg",
            "https://i.imgur.com/641fRAZ.jpg",
            "https://images.plurk.com/4Wr1If26wnRKEZIllQVIzO.jpg",
            "https://images.plurk.com/2OkhSDoYeOsQGdvb5KM9Pn.jpg",
            "https://images.plurk.com/3czlRTuYeTYqCj5vicDQBq.png",
            "https://images.plurk.com/1M3oSnXNOMVxnOose7Wh8v.jpg",
            "https://images.plurk.com/1NiFD84tWntjhd65rqpofb.png"
        ]
        rand_num = random.randint(0, 10)
        if rand_num == 0:
            return random.choice(wara_imgs) + ' \n笑死'
        elif rand_num == 1:
            return '哭啊'
        else:
            return '笑死'


    def comet_main(self):
        while self.main_flag:
            q = {'offset':  self.offset}

            resp = requests.get(self.comet_server_url, params=q)

            if resp.status_code != 200:
                loguru.logger.error('RESP: status code is not 200')
                continue
            # loguru.logger.success('RESP: success')

            comet_content = resp.text

            m = re.search(r'CometChannel.scriptCallback\((.*)\);', comet_content)
            json_content = json.loads(m.group(1))
            if "data" in json_content:
                self.comet_callBack(json_content["data"])

            if "new_offset" in json_content:
                offset = json_content["new_offset"]


    def comet_callBack(self, data):
        for d in data:
            if 'type' not in d:
                loguru.logger.warning(json.dumps(d))
                continue
            if d['type'] == 'new_plurk':
                if not self.is_friend(d["user_id"]):
                    # Not friend, jump
                    continue

                if "不要笑" in d["content"]:
                    res = self.add_user(d["user_id"])
                    if res: loguru.logger.info("Stop user " + str(d["user_id"]))
                elif "好笑嗎" in d["content"]:
                    res = self.remove_user(d["user_id"])
                    if res: loguru.logger.info("Reset user " + str(d["user_id"]))

                if self.if_user(d["user_id"]):
                    continue
                else:
                    opt = {
                        'plurk_id': d['plurk_id'],
                        'qualifier': ':',
                        'content': self.gen_msg()
                    }
                    loguru.logger.info("Response to " + str(opt["plurk_id"]))
                    resp = self.plurk.callAPI("/APP/Responses/responseAdd", options=opt)


    def routine_main(self):
        def add_all_friends():
            self.plurk.callAPI("/APP/Alerts/addAllAsFriends")

        def refresh_channel():
            user_channel = self.plurk.callAPI("/APP/Realtime/getUserChannel")
            self.comet_server_url = user_channel["comet_server"]
            self.offset = 0
            loguru.logger.info("Refresh comet channel")

        schedule.every(5).seconds.do(add_all_friends)
        schedule.every(20).minutes.do(refresh_channel)
        while self.main_flag:
            schedule.run_pending()
            time.sleep(1)

    def main(self):
        try:
            comet_proc = Process(target=self.comet_main, daemon=True)
            routine_proc = Process(target=self.routine_main, daemon=True)
            comet_proc.start()
            routine_proc.start()
            while True: time.sleep(100)
        except (KeyboardInterrupt, SystemExit):
            comet_proc.terminate()
            routine_proc.terminate()
            loguru.logger.info("Stop bot.")

if __name__=="__main__":
    loguru.logger.add(
        f'data/{datetime.date.today():%Y%m%d}.log',
        rotation='1 day',
        retention='7 days',
        level='DEBUG')
    bot = Bot("token.txt", "data/users.db")
    bot.main()
