from flask import Flask
 
app = Flask(__name__)

@app.route("/home")
def home():
    return "<h1>Hello from Docker!</h1><p>Welcome to my first Flask app.</p>"
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)