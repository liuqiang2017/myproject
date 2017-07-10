'''
Created on 2017.1.8

@author: lq

'''
import os
import time
import uuid
import json
import Queue
from time import sleep
from config import load_config
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)
config = load_config()

class master():
    def __init__(self, num = 3):
        self.queue = Queue.Queue(10)
        self.accountInfo = {}
        self.infoList = config.ACCOUNTLIST
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

    def waitCondition(delayTime, timeOut, condition):
	tm = 0
	assert(delayTime > 0) 
	assert(timeOut > delayTime)
	while tm < timeOut:
            if condition(tm):
                return True
            tm = tm + delayTime
            time.sleep(delayTime)
        return False 

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
                return json.dumps({"error": "all accounts are in use"})
            guuid = self.queue.get()
            acc = self.accountInfo[guuid]
            del self.accountInfo[guuid]
            return json.dumps(acc)
        elif request.method == 'POST':
            li = [] 
            li.append(json.loads(request.data))
            self.addInfo(self.accountInfo, self.queue, li)
            return request.data
        return json.dumps({"error": "request error"})


if __name__ == '__main__':
    obj = master()
    obj.run()
