'''
Created on 2017.1.8

@author: lq
'''
import threading
import Queue
from time import sleep
from flask import Flask 
app = Flask(__name__)

class master():
    def __init__(self, num = 3):
        self.queue = Queue.Queue  
        self.threadList = []
        self.threadNum = num
    
    def run(self):
        #start thread
        for i in range(self.threadNum):
            self.threadList.append(threading.Thread(target=self.processThreadFunc, args = ()))
        for p in self.threadList:
            p.start()
            
        app.add_url_rule('/hello', 'hello', self.msgTransformationFunc, methods = ['GET', 'POST'])
        app.run(host='0.0.0.0', port='12345')
    
    def msgTransformationFunc(self):
        return 'hello word'
       
    def processThreadFunc(self):
        while True:
            sleep(3)
            pass
       
    
if __name__ == '__main__':
    obj = master()
    obj.run()
