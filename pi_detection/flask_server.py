from flask import Flask, send_file, jsonify, request, Response, render_template
from PIL import Image
import io
import time
import os
from stat import S_ISREG, ST_CTIME, ST_MODE
from cv2 import imencode

class Flask_Server: 

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

        
        def get_frame():
            while True:
                if not queue1.empty():
                    frame = queue1.get()
                    ret, frame_en = imencode(".jpg", frame)
                    yield (b'--frame\r\n' 
                        b'Content-Type: image/jpeg\r\n\r\n' + bytearray(frame_en) + b'\r\n')

        

        app.run(host='0.0.0.0')

