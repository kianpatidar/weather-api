from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def hello_world():
    return jsonify({"message": "Hello_world"})


@app.route("/user")
def user():
    return jsonify({"name": "kiran",
                    "age": 30,
                    'city': 'ABC'})


@app.route("/hello/<name>")
def greet(name):
    return f"Hello, {name}!"


@app.route("/add")
def add():
    a = int(request.args.get("a",0))
    b = int(request.args.get("b",0))
    return {"sum": a+b}



if __name__ == "__main__":
    app.run(debug=True)

