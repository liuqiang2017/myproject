'''
Created on 2017.1.8

@author: lq
'''
import threading
import Queue
from flask import Flask
app = Flask(__name__)

class master():
    def __init__(self):
        self.queue = Queue.Queue  
        pass
    
    def run(self):
        app.add_url_rule('/hello', 'hello', self.hello, methods = ['GET', 'POST'])
        app.run(host='0.0.0.0', port='12345')
    
    def processThreadFunc(self) :
        return 'hello word'
    
if __name__ == '__main__':
    obj = master()
    obj.run()
