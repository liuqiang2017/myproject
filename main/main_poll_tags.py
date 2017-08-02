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
from ding_talk import Ding

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

    def byteify(self, obj):
        if isinstance(obj, dict):
            res = {}
            for key, value in obj.iteritems():
                res = dict(res, **{self.byteify(key): self.byteify(value)})
            return res
            #return {self.byteify(key): self.byteify(value) for (key, value) in obj.iteritems()}
        elif isinstance(obj, list):
            res = []
            for i in obj:
               res.append(self.byteify(i))
            return res
            #return [self.byteify(element) for element in obj]
        elif isinstance(obj, unicode):
            return obj.encode('utf-8')
        else:
            return obj

    #add acc in queue
    def addAccountsInQueue(self, ac, qu, li):
        for item in li:
            item = self.byteify(item)
            acc = dict(admin=item['admin'], password=item['password'])
            #ac available dict
            global mutex
            try:
                if mutex.acquire():
                    if acc not in ac.values():
                        # set accounts, only 
                        if acc in self.infoList:                
                            logging.info("-------------add acc to available queue------------")
                            logging.info(str(acc))
                            guuid = uuid.uuid1()
                            ac[guuid] = acc
                            qu.put(guuid)
                    mutex.release()
            except Exception as e:
                logging,info(e)
                mutex.release()
    def run(self):
        #start thread
        pf = threading.Thread(target=self.addAccInPollListFunc, args = ())
        p = threading.Thread(target=self.infoReportThread, args=())
        p.start()
        pf.start()

        app.add_url_rule('/account', 'account', self.msgTransformFunc, methods = ['GET', 'POST'])
        app.add_url_rule('/bindAcc', 'bindAcc', self.bindFunc, methods = ['POST'])
        app.run(host='0.0.0.0', port='12345')

    def infoReportThread(self):
        logging.info("------info report thread start------ ")
        while True:
            logging.info("--------------available accounts------------------")
            for item in self.accountInfo.values():
                logging.info(item)
            time.sleep(120)

    #timeout thread
    def addAccInPollListFunc(self):
        logging.info("------timeout thread start------")
        while True:
            time.sleep(1)
            try:
                for index, item in enumerate(self.timeoutPollList):
                    if item["timeout"]<1:
                        self.timeoutPollList.remove(item)
                        acc = item["account"]
                        warnStr = "Account occupancy timeout, case:{0}, acc:{1}".format(item.get('case', 'invalued'), acc['admin'])
                        Ding(warnStr)
                        li = []
                        li.append(acc)
                        logging.warning("------Timeout------")
                        logging.warning(acc)
                        self.addAccountsInQueue(self.accountInfo, self.availableAccQu, li)
                    self.timeoutPollList[index]["timeout"] = self.timeoutPollList[index]["timeout"] -1
            except IndexError:
                pass
            except Exception as e:
                logging.warning(e) 
    #bind func
    def bindFunc(self):
        logging.info("---------------------bind acc and case ---------------------")
        if request.method == 'POST':
            res = {}
            flag = False
            res = json.loads(request.data)
            res = self.byteify(res)
            for i, item in enumerate(self.timeoutPollList):
                if item['account']['admin']==res['admin']:
                    try:
                        self.timeoutPollList[i]["case"] = res['case']
                        flag = True
                        break
                    except IndexError:
                        pass
	    if flag:
                logging.info('bind success! case info:{0}, acc info: {1}'.format(res['case'], res['admin']))
            else:
                logging.warning('bing failed!  case info:{0}, acc info: {1}'.format(res['case'], res['admin']))
                return json.dumps({'code': 500, 'msg': "acc  {0} not exist in polling list".format(res['admin'])})
            return json.dumps({'code': 200, 'msg': ""})
        else:
            return json.dumps({'code':400,'msg':'request error'})
            
                
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
            res = {}
            res = json.loads(request.data)
            res = self.byteify(res)
            li.append(res)            
            logging.info("---------------------release acc-----------------------")
            logging.info(res)
            for item in self.timeoutPollList:
		if res['admin'] == item["account"]['admin']:
		    self.timeoutPollList.remove(item)
                    break
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
