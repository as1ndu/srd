import os
import base64
from flask import Flask, request, jsonify

app = Flask(__name__)

# Command line interface
def cli(cmd):
    stream = os.popen('tree')
    output = stream.read()
    return output

# Reconstruct scilla file via REST
def scilla_file(filename, source):
    path = "{0}".format(filename)

    with open(path, 'w') as f:
        f.write(source)
    print("* {0} saved to disk.".format(filename))
       
    return filename

# Warnings & Error messages
def messages(filename, gas_limit):
    command = "./scilla-checker  -libdir scilla/bin/stdlib -gaslimit "  + gas_limit + " " + filename + "-jsonerrors"
    messages = cli(command)
    return messages

# Gas usage analyser
def gas_usage(filename, gas_limit):
    command = "./scilla-checker  -libdir scilla/bin/stdlib -gaslimit "  + gas_limit + " " + filename + "-jsonerrors"
    gas_usage = cli(command)
    return gas_usage

# Cash flow analysis
def cashflow_ananysis(filename, gas_limit):
    command = "./scilla-checker -cf -libdir scilla/bin/stdlib -gaslimit "  + gas_limit + " " + filename + "-jsonerrors"
    cashflow_ananysis = cli(command)
    return cashflow_ananysis


@app.route("/debug", methods=["POST"])
def debug():
    # Only allow post requests
    if request.method == 'POST':

        #read POST request data
        filename = str(request.values.to_dict(flat=False)['filename'][0])
        gas_limit = str(request.values.to_dict(flat=False)['gas_limit'][0])
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
        "messages": messages(filename, gas_limit),
        "gas_usage": gas_usage(filename, gas_limit),
        "cashflow_analysis": cashflow_ananysis(filename, gas_limit),
        "scilla_version": 0
    }

    data = jsonify(payload) # Convert data to json

    return data

if __name__ == "__main__":
    app.run(debug=True)
