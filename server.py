from flask import Flask, request

app = Flask(__name__) 

@app.route("/debug", methods=["GET", "POST"])
def debug():
    data = str(request.values.to_dict(flat=False))
    return data