"""
Plurk Bot core

Distributed under terms of the WTFPL license.
"""

from poaurk import PlurkAPI
from multiprocessing import Process, Value
import typing
import requests
import json
import re
import loguru
import datetime
import time
import schedule
import sqlite3

COMET_RETRY = 100
COMET_MAX_TRY = 10

class Bot:
    def __init__(self, token_file, database, msg_func):

        self.offset = 0
        self.database = database
        self.gen_msg = msg_func

        self.plurk = PlurkAPI.fromfile(token_file)
        if self.init_comet() == -1:
            return

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

    def init_comet(self):
        status, user_channel = self.plurk.callAPI("/APP/Realtime/getUserChannel")
        if status:
            self.comet_server_url = user_channel["comet_server"]
            self.comet_server_url = self.comet_server_url.split('?')[0].split('#')[0]
            self.channel_name = user_channel["channel_name"]
            self.offset = 0
            loguru.logger.info(f"Start pulling from comet server: {self.comet_server_url}, channel: {self.channel_name}")
            return 0
        else:
            loguru.logger.error("Get comet channel failed")
            return -1

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
        status, resp = self.plurk.callAPI("/APP/Profile/getPublicProfile", options=opt)
        if not status:
            loguru.logger.error(resp)
            return None

        return resp["are_friends"]

    def base36encode(self, number, alphabet='0123456789abcdefghijklmnopqrstuvwxyz'):
        """Converts an integer to a base36 string."""
        if not isinstance(number, int):
            raise TypeError('number must be an integer')

        base36 = ''
        sign = ''

        if number < 0:
            sign = '-'
            number = -number

        if 0 <= number < len(alphabet):
            return sign + alphabet[number]

        while number != 0:
            number, i = divmod(number, len(alphabet))
            base36 = alphabet[i] + base36

        return sign + base36

    def comet_main(self):
        error = False
        retry = 0
        offset_duplicate = 0
        while 1:
            if retry > COMET_RETRY:
                self.init_comet()
                retry = 0

            if offset_duplicate > COMET_MAX_TRY:
                self.init_comet()
                offset_duplicate = 0

            q = {
                'channel': self.channel_name,
                'offset':  self.offset
            }

            try:
                resp = requests.get(self.comet_server_url, params=q, timeout=60)
                resp.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                loguru.logger.error(f"Http Error: {errh}")
                error = True
            except requests.exceptions.ConnectionError as errc:
                loguru.logger.error(f"Error Connecting: {errc}")
                error = True
            except requests.exceptions.Timeout as errt:
                loguru.logger.error(f"Timeout Error: {errt}")
                error = True
            except requests.exceptions.RequestException as err:
                loguru.logger.error(f"Request Other Error: {err}")
                error = True

            if error:
                time.sleep(5)
                retry += 1
                error = False
                continue

            retry = 0

            loguru.logger.debug(f"Request url: {resp.url}")
            comet_content = resp.text

            m = re.search(r'CometChannel.scriptCallback\((.*)\);', comet_content)
            try:
                json_content = json.loads(m.group(1))
            except Exception as err:
                loguru.logger.error(f"Json Error: {err}")

            try:
                if "data" in json_content:
                    self.comet_callBack(json_content["data"])
            except Exception as err:
                loguru.logger.error(f"Callback Error: {err}")

            try:
                if "new_offset" in json_content:
                    if self.offset == json_content["new_offset"]:
                        offset_duplicate += 1
                    else
                        offset_duplicate = 0
                    self.offset = json_content["new_offset"]
                    # loguru.logger.debug(f"Update Offset: {self.offset}")
                    if self.offset<0:
                        loguru.logger.error(f"Offset Error: {self.offset}")
                        self.init_comet()
            except Exception as err:
                loguru.logger.error(f"Offset Error: {err}")
            time.sleep(5)

    def comet_callBack(self, data):
        for d in data:
            if 'type' not in d:
                loguru.logger.warning(json.dumps(d))
                continue
            if d['type'] == 'new_plurk':
                if not self.is_friend(d["user_id"]):
                    # Not friend, jump
                    continue

                if "不好笑" in d["content"]:
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
                    plurk_id_base36 = self.base36encode(opt['plurk_id'])
                    loguru.logger.info(f"Response to https://www.plurk.com/p/{plurk_id_base36}")
                    self.plurk.callAPI("/APP/Responses/responseAdd", options=opt)


    def routine_main(self):
        def add_all_friends():
            self.plurk.callAPI("/APP/Alerts/addAllAsFriends")

        def knock_comet():
            knock_comet_url = "https://www.plurk.com/_comet/generic"
            p = {
                'channel': self.channel_name
            }
            try:
                resp = requests.get(knock_comet_url, params=p, timeout=60)
                resp.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                loguru.logger.error(f"Http Error: {errh}")
                return
            except requests.exceptions.ConnectionError as errc:
                loguru.logger.error(f"Error Connecting: {errc}")
                return
            except requests.exceptions.Timeout as errt:
                loguru.logger.error(f"Timeout Error: {errt}")
                return
            except requests.exceptions.RequestException as err:
                loguru.logger.error(f"Request Other Error: {err}")
                return
            except Exception as err:
                loguru.logger.error(f"Other Error: {err}")
                return

            loguru.logger.debug(f"Request url: {resp.url}")

        schedule.every(1).minutes.do(add_all_friends)
        schedule.every(1).minutes.do(knock_comet)

        while 1:
            try:
                schedule.run_pending()
            except Exception as err:
                loguru.logger.error(f"Schedule Task Error: {err}")

            # Enter a long sleep
            time.sleep(30)

    def main(self):
        comet_proc = Process(target=self.comet_main, daemon=True)
        routine_proc = Process(target=self.routine_main, daemon=True)
        try:
            comet_proc.start()
            routine_proc.start()
            while 1:
                time.sleep(600)
                loguru.logger.debug(f"Running... Comet: {comet_proc.is_alive()}, Routine: {routine_proc.is_alive()}")
        except (KeyboardInterrupt, SystemExit):
            comet_proc.terminate()
            routine_proc.terminate()
            loguru.logger.info("Stop bot.")
