'''
Created on 2017.1.8

@author: lq

'''
import sys
import time
import uuid
import json
import logging
import Queue
import threading
from config import load_config
from logging.handlers import RotatingFileHandler
from flask import Flask, request
app = Flask(__name__)
config = load_config()

mutex = threading.Lock()

class master():
    def __init__(self):
        self.threadList = []
        self.timeoutPollList = []
        self.availableAccQu= Queue.Queue()
        self.accountInfo = {}
        self.infoList = config.accounts_list
        self.timeout =  config.acc_timeout
        self.addAccountsInQueue(self.accountInfo, self.availableAccQu, self.infoList)

    #add acc in queue
    def addAccountsInQueue(self, ac, qu, li):
        global mutex
        try:
            for item in li:
                #ac available dict
                if item not in ac.values():
                    # set accounts, only 
                    if item in self.infoList:                
                        logging.info("-------------add acc to available queue------------")
                        logging.info(str(item))
                        guuid = uuid.uuid1()
                        qu.put(guuid)
                        if mutex.acquire():
                            ac[guuid] = item
                            mutex.release()
        except Exception as e:
            logging(e)
            mutex.release()
    def run(self):
        #start thread
        pf = threading.Thread(target=self.addAccInPollListFunc, args = ())
        p = threading.Thread(target=self.infoReportThread, args=())
        p.start()
        pf.start()

        app.add_url_rule('/account', 'account', self.msgTransformFunc, methods = ['GET', 'POST'])
        app.run(host='0.0.0.0', port='12345')

    def infoReportThread(self):
        logging.info("------info report thread start------ ")
        while True:
            logging.info("--------------available accounts------------------")
            for item in self.accountInfo.values():
                logging.info(item)
            time.sleep(60)

    #timeout thread
    def addAccInPollListFunc(self):
        logging.info("------timeout thread start------")
        while True:
            time.sleep(1)
            try:
                for index in range(len(self.timeoutPollList)):
                    if self.timeoutPollList[index]["timeout"]<1:
                        acc = self.timeoutPollList[index]["account"]
                        del self.timeoutPollList[index]
                        li = []
                        li.append(acc)
                        logging.warning("------Timeout, release acc------")
                        logging.warning(acc)
                        self.addAccountsInQueue(self.accountInfo, self.availableAccQu, li)
                    self.timeoutPollList[index]["timeout"] = self.timeoutPollList[index]["timeout"] -1
            except IndexError:
                pass
            except Exception as e:
                logging.warning(e)
                
    def byteify(self, input):
        if isinstance(input, dict):
            return {self.byteify(key): self.byteify(value) for key, value in input.iteritems()}
        elif isinstance(input, list):
            return [self.byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input

    #data process func    
    def msgTransformFunc(self):
        if request.method == 'GET':
            acc = {}
            if self.availableAccQu.empty():
                logging.warning('all accounts are in ues[msgTransformFunc]')
                return json.dumps({"error": "all accounts are in use"})
            #get acc from local dict
            guuid = self.availableAccQu.get()
            acc = self.accountInfo[guuid]
            #add to in use que
            logging.info("----------------------get acc---------------------")
            logging.info(acc["admin"])
            self.accountInfo.pop(guuid)
            self.timeoutPollList.append(dict(timeout=self.timeout, account=acc))
            return json.dumps(acc)
        elif request.method == 'POST':
            li = []
            #li.append(json.loads(request.data))
            li.append(self.byteify(json.loads(request.data)))            
            logging.info("---------------------release acc-----------------------")
            logging.info(json.loads(request.data)["admin"])
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
