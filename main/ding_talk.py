# -*- coding: utf-8  -*-

import json
from requests import post as requests_post

access_token = 'xxxx'

class DingTalk(object):
    url = 'https://oapi.dingtalk.com/robot/send'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    def __init__(self, access_token, url=None):
        if url is not None:
            self.url = url
        self.access_token = access_token

    def send(self, json_data):
        req = requests_post(self.url, data=json.dumps(json_data),
                            headers=self.headers,
                            params={'access_token': self.access_token})
        return req.json()

    def text_message(self, text, at=[], at_all=False):
        json_data = {
            "msgtype": "text",
            "text": {
                "content": text
            }
        }
        if at or at_all:
            if not isinstance(at, list):
                at = [at]

            json_data['at'] = {
                "atMobiles": at,
                "isAtAll": at_all
            }

        return self.send(json_data)
    def link_message(self, title='', text='', message_url='', pic_url=''):
        json_data = {
            "msgtype": "link",
            "link": {
                "title": title,
                "text": text,
                "picUrl": pic_url,
                "messageUrl": message_url
            }
        }
        return self.send(json_data)

    def markdown_message(self, title, text):
        json_data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": text
            }
        }
        return self.send(json_data)

def usage():
    return '''1. dingtalk "content for output"
              2. dingtalk "content for output" warn|info telephone
              3. dingtalk "content for output" critical'''

def Ding(content, lvl='warn', tel=''):
    ding_talk = DingTalk(access_token)
    if tel == '' and lvl != 'critical':     
        ding_talk.text_message(content)
    elif tel != '' and lvl != 'critical':
        ding_talk.text_message(content, at=[tel])
    elif lvl == 'critical':
        ding_talk.text_message(content, at_all=True)
    else:
        print usage()

if __name__ == '__main__':
    #Ding("a s & *", lvl='error')
    #Ding("a s & *")
    #Ding("a s & *", tel='15857169861')
    #Ding("a s & *", lvl='critical')