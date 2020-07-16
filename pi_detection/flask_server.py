from flask import Flask


class Flask_Server: 

    def start(self, queue1, queue2):
        app = Flask(__name__)
        @app.route("/")
        @app.route("/home")
        def home():
            msg = 'server running'
            while True:
                if not queue1.empty():
                    msg = queue1.get()
                    queue1.empty()
                    return msg
                    
            
                    
            


        @app.route("/about")
        def about():
            return "<h1>About Page</h1>"


        app.run(host='0.0.0.0')


