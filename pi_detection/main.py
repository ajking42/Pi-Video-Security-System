from multiprocessing import Process,Queue,Pipe
from flask_server import Flask_to_android_server


def run(self)
    detector = Detector()
    server = Flask_to_android_server()
    
    parent_conn,child_conn = Pipe()
    p = Process(target=detector.detect, args=(child_conn,))
    p.start()
    print(parent_conn.recv())

    server.process_detection(parent_conn.recv())