'''
Created on 2017.1.8

@author: lq

'''
import os
import uuid
import json
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import threading
import Queue
from time import sleep

app = Flask(__name__)

class master():
    def __init__(self, num = 3):
        self.queue = Queue.Queue(10)
        self.accountInfo = {}
        self.infoList = [{"a": "a"}, {"b": "b"}]
        self.addInfo(self.accountInfo, self.queue, self.infoList)

    def addInfo(self, ac, qu, li):
        for item in li:
            if item not in ac.values():
                if item in self.infoList:
                    print item
                    guuid = uuid.uuid1()
                    qu.put(guuid)
                    ac[guuid] = {}
                    ac[guuid].update(item)

    def run(self):
        #start thread
        #for i in range(self.threadNum):
        #    self.threadList.append(threading.Thread(target=self.processThreadFunc, args = ()))
        #for p in self.threadList:
        #    p.start()

        app.add_url_rule('/account', 'account', self.msgTransformFunc, methods = ['GET', 'POST'])
        app.run(host='0.0.0.0', port='12345')

    def msgTransformFunc(self):
        if request.method == 'GET':
            acc = {}
            if self.queue.empty():
                return json.dumps({"error": "accounts is in use"})
            guuid = self.queue.get()
            acc = self.accountInfo[guuid]
            del self.accountInfo[guuid]
            return json.dumps(acc)
        elif request.method == 'POST':
            li = [] 
            li.append(json.loads(request.data))
            self.addInfo(self.accountInfo, self.queue, li)
            return request.data
        return 'request error'


if __name__ == '__main__':
    obj = master()
    obj.run()
