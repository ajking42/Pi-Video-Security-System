from flask import Flask
from datetime import datetime


class Flask_Server:


    def start_server(self, q1, q2):
        app = Flask(__name__)

        @app.route('/')
        def index():
            return 'This server is doing stuff lol'
            
        def process_detection(self, detection):
                    @app.route('/')
                        def index():
                            return '{} detected at {}'.format(detection, datetime.now())
        if __name__ == '__main__':
            app.run(debug=True, host='0.0.0.0')

    