'''
Created on 2017.1.8

@author: lq

'''
import os
import sys
import time
import uuid
import json
import logging
import Queue
import threading
from time import sleep
from config import load_config
from logging.handlers import RotatingFileHandler
from flask import Flask, request
app = Flask(__name__)
config = load_config()


mutex = threading.Lock()

class master():
    def __init__(self, num = 3):
        self.li = []
        self.threadNum = num
        self.threadList = []       
        self.availableAccQu= Queue.Queue()
        self.queueInUse = Queue.Queue()
        self.accountInfo = {}
        self.infoList = config.ACCOUNTLIST
        self.addAccountsInQueue(self.accountInfo, self.availableAccQu, self.infoList)
    
    #add acc in queue
    def addAccountsInQueue(self, ac, qu, li):
        global mutex
        if mutex.acquire():
            for item in li:
                #ac available dict
                if item not in ac.values():
                    # set accounts, only 
                    if item in self.infoList:
                        print item
                        guuid = uuid.uuid1()
                        qu.put(guuid)
                        ac[guuid] = item
            print "##init:", self.accountInfo
            print "ac:", ac
            mutex.release()

    #polling interface
    def waitCondition(self, delayTime, timeOut, condition, msg = ""):
	tm = 0
	assert(delayTime > 0) 
	assert(timeOut > delayTime)
	while tm < timeOut:
            if condition(tm):
                if msg != "":
                    logging.info(msg)
                return True
            tm = tm + delayTime
            time.sleep(delayTime)
        return False 

    def run(self):
        #start thread
        for i in range(self.threadNum):
            self.threadList.append(threading.Thread(target=self.timeoutProcessThreadFunc, args = ()))
        for p in self.threadList:
            p.start()

        app.add_url_rule('/account', 'account', self.msgTransformFunc, methods = ['GET', 'POST'])
        app.run(host='0.0.0.0', port='12345')
    
    #timeout thread
    def timeoutProcessThreadFunc(self):
        logging.info("timeout thread start.")
        while True:
            acc = self.queueInUse.get()
            print "###############################acc in time out",acc
            logging.info(acc["admin"] + " is in use[timeoutProcessThreadFunc]")
            condition = lambda s:acc in self.accountInfo.values()
            msg = acc["admin"] + " was released."
            result = self.waitCondition(1, 5, condition, msg)
            print "result $$$$$$",result
            logging.info("timeout_func:", self.accountInfo)
            if not result:
                logging.warning("timeout, release acc:" + acc["admin"])
                self.li.append(acc)
                print "li in timeout:",self.li
                self.addAccountsInQueue(self.accountInfo, self.availableAccQu, self.li)
                self.li.remove(acc)
    #data process func    
    def msgTransformFunc(self):
        print ("get_func:",self.accountInfo)
        if request.method == 'GET':
            acc = {}
            if self.availableAccQu.empty():
                logging.info('error: all accounts are in ues[msgTransformFunc]')
                return json.dumps({"error": "all accounts are in use"})
            #get acc from local dict
            guuid = self.availableAccQu.get()
            acc = self.accountInfo[guuid]
            #add to in use que
            print "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq",acc
            self.queueInUse.put(acc)

            logging.info("get acc:" + acc["admin"])
            del self.accountInfo[guuid]
            return json.dumps(acc)
        elif request.method == 'POST':
            li = [] 
            li.append(json.loads(request.data))
            logging.info("release acc:" + json.loads(request.data)["admin"])
            self.addAccountsInQueue(self.accountInfo, self.availableAccQu, li)
            return request.data
        return json.dumps({"error": "request error"})


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=sys.path[0] + '/log.log',
                filemode='w')
    
    Rthandler = RotatingFileHandler('log.log', maxBytes=2*1024*1024,backupCount=5)
    Rthandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    Rthandler.setFormatter(formatter)
    logging.getLogger('').addHandler(Rthandler)
    
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)
    logging.getLogger('').addHandler(streamHandler)

    obj = master()
    obj.run()
