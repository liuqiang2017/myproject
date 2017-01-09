'''
Created on 2017.1.8

@author: lq
'''
import threading
import Queue
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'hello world'

@app.route('/laoqi')
def hello():
    return 'let is sleep laoqi'

class master():
    def __init__(self):
        self.queue = Queue.Queue  
        pass
    
    def run(self):
        pass
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='12345')
