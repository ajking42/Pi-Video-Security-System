from flask import Flask, send_file, jsonify, request
from PIL import Image
import io
import time
import os
from stat import S_ISREG, ST_CTIME, ST_MODE

class Flask_Server: 

    def start(self, queue1, queue2):
        app = Flask(__name__)

        @app.route("/", methods = ['GET', 'POST'])
        @app.route("/home", methods = ['GET', 'POST'])
        def home(): 
            msg = 'server running'
            
            detection_dir_path = 'detection_storage/'

            detection_file_names = []

            #all entries in the directory w/ stats
            data = (os.path.join(detection_dir_path, fn) for fn in os.listdir(detection_dir_path))
            data = ((os.stat(path), path) for path in data)

            # regular files, insert creation date
            data = ((stat[ST_CTIME], path)
                    for stat, path in data if S_ISREG(stat[ST_MODE]))

            for cdate, path in sorted(data):
                print(time.ctime(cdate), os.path.basename(path))
                detection_file_names.append(os.path.basename(path))
            
            
            return jsonify(detection_file_names)


        
        @app.route("/selectedimage", methods=['GET','POST'])
        def selected_image():  
            file_name = request.json['filename']
            image_path = f'detection_storage/{file_name}'
            
            

            return send_file(image_path, mimetype='image/PNG')


        app.run(host='0.0.0.0')