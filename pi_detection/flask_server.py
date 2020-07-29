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

            detection_file_names = []

            # Get a list of all files in /detection_storage, and their statuses
            data = (os.path.join(detection_dir_path, fn) for fn in os.listdir(detection_dir_path))
            data = ((os.stat(path), path) for path in data)

            # Get creation dates for each file
            data = ((stat[ST_CTIME], path)
                    for stat, path in data if S_ISREG(stat[ST_MODE]))

            #Sort files by creation date, then append the path name to detection_file_names
            for cdate, path in sorted(data):
                detection_file_names.append(os.path.basename(path))
            
            # Return jsonified list of sorted file names
            return jsonify(detection_file_names)


        
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

