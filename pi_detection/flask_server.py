from flask import Flask, send_file, send_from_directory, jsonify, request, Response, render_template
from PIL import Image
import io
import time
import os
import signal
import pickle
import yaml
from stat import S_ISREG, ST_CTIME, ST_MODE
from cv2 import imencode
import firebase_admin
from firebase_admin import messaging, credentials
from datetime import datetime, timedelta
from multiprocessing import Process, Queue

class Flask_Server: 
    config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader) 


    # Start server running
    def start(self, queue1, queue2):
        app = Flask(__name__)

        

        @app.route("/", methods = ['GET', 'POST'])
        @app.route("/home", methods = ['GET', 'POST'])
        def home(): 
            # Currently used to retrieve a list of detection frames in order of
            # file creation date

            msg = 'server running'
            
            detection_dir_path = 'detection_storage/'

            detection_file_names = os.listdir(detection_dir_path)

            # get file creation dates
            frames = ((os.path.getctime(f'{detection_dir_path}{frame}'), frame) for frame in detection_file_names)
            
            sorted_detections = []

            # sort file names by creation date
            for date, frame in sorted(frames):
                sorted_detections.append(frame)

            return jsonify(sorted_detections)

        @app.route("/recordings_list", methods = ['GET', 'POST'])
        def recordings_list(): 
            # Currently used to retrieve a list of detection frames in order of
            # file creation date

            msg = 'server running'
            
            video_dir_path = 'video_storage/'

            video_file_names = os.listdir(video_dir_path)

            # get file creation dates
            recordings = ((os.path.getctime(f'{video_dir_path}{frame}'), frame) for frame in video_file_names)
            
            sorted_recordings = []

            # sort file names by creation date
            for date, recording in sorted(recordings):
                sorted_recordings.append(recording)

            return jsonify(sorted_recordings)


        @app.route("/video_storage/<video_url>", methods=['GET','POST'])
        def video_storage(video_url):  
            # Recieves detection file name from android app and returns 
            # the equivalent file
            video_path = f"video_storage/{video_url}"
            
            os.system(f"ffmpeg -i {video_path} -vcodec libx264 {video_path}.mp4")
            return send_from_directory('video_storage/', video_url, as_attachment=True)
        


        @app.route("/detection_storage/<image_url>", methods=['GET', 'POST'])
        def detection_storage(image_url):

            return send_from_directory('detection_storage/', image_url, as_attachment=True)

        @app.route("/update_yaml", methods=['POST'])
        def update_yaml():
            config_json = request.json

            print(config_json)
            ff = open("config.yaml", "w+")


            yaml.dump(config_json, ff, allow_unicode=True)  

            print('Terminating server...')

            os.kill(os.getpid(), signal.SIGINT)
            

            return "JSON recieved"


        
        @app.route("/selectedimage", methods=['GET','POST'])
        def selected_image():  
            # Recieves detection file name from android app and returns 
            # the equivalent file
            file_name = request.json['filename']
            image_path = f'detection_storage/{file_name}'
            
            

            return send_file(image_path, mimetype='image/PNG')

            

        @app.route("/streaming")
        def streaming():
            return Response(get_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


        @app.route("/setToken", methods=['GET','POST'])
        def setToken():
            # Saves the token required by firebase cloud messaging
            deviceToken = request.form['token']
            print(deviceToken)
            with open('deviceToken.txt', 'wb') as f:
                pickle.dump(deviceToken, f)
           
            return "Success"


        
        def get_frame():
            while True:
                if not queue1.empty():
                    frame = queue1.get()
                    ret, frame_en = imencode(".jpg", frame)
                    yield (b'--frame\r\n' 
                        b'Content-Type: image/jpeg\r\n\r\n' + bytearray(frame_en) + b'\r\n')
        
        

        app.run(host='0.0.0.0')


    def notification(self, queue):
        
        # Initialise firebase_admin
        cred = credentials.Certificate("pi-app-32d2a-firebase-adminsdk-7x9v9-7d3ffffe80.json")
        default_app = firebase_admin.initialize_app(cred)

        # Get first detections and times
        current_time = datetime.now()
        next_notification_time = current_time

        # Get device token variable
        with open('deviceToken.txt', 'rb') as f:
                deviceToken = pickle.load(f)


        last_detection = ""
        while True:
            detection = queue.get()
            current_time = datetime.now()
            if detection != last_detection or current_time > next_notification_time:
                last_detection = detection

                title = detection + ' detected!'
                body = current_time.strftime("%m-%d-%Y, %H:%M:%S")
                # See documentation on defining a message payload.
                message = messaging.Message(notification=messaging.Notification(title=title, body=body), token=deviceToken)

                # Send a message to the device corresponding to the provided
                # registration token.
                response = messaging.send(message)
                # Response is a message ID string.
                print('Sent message:', response)
                

                # Ensure repeat notification isn't sent for a number of seconds
                next_notification_time = datetime.now() + timedelta(seconds=self.config['notify_period'])

                    




