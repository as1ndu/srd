import os
import base64
from flask import Flask, request, jsonify


app = Flask(__name__)

# Command line interface
def cli(cmd, filename):
    stream = os.popen('tree')
    output = stream.read()
    return output

# Reconstruct scilla file via REST
def scilla_file(filename, source):
    path = "{0}".format(filename)

    with open(path, 'w') as f:
        f.write(source)

    print("* {0} saved to disk.".format(filename))
       
    return ""

# Warnings & Error messages
def messages(filename):
    return "Messages processed"

# Gas usage analyser
def gas_usage(filename):
    return "Gas usage analysis"

# Cash flow analysis
def cashflow_ananysis(filename):
    return "Cash flow analyser"


@app.route("/debug", methods=["POST"])
def debug():
    # Only allow post requests
    if request.method == 'POST':

        #read POST request data
        filename = str(request.values.to_dict(flat=False)['filename'][0])
        source = str(request.values.to_dict(flat=False)['source'][0])

        # decode scilla source
        decoded_source = str(base64.b64decode(source)).encode().decode("unicode-escape")
        decoded_source = decoded_source.replace("b\'","",1)
        valid_source =  decoded_source[:len(decoded_source)-1]

        # Save scilla file to disk
        scilla_file(filename,   valid_source)

        print("debugged {0} ".format(filename))

    payload = {
        "filename": filename,
        "messages": messages(''),
        "gas_usage": gas_usage(''),
        "cashflow_analysis": cashflow_ananysis('')
    }

    data = jsonify(payload) # Convert data to json

    return data
