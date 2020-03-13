import os
import json
import base64
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

# Command line interface
def cli(cmd):
    stream = os.popen(cmd)
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
    command = "scilla-checker -cf -typeinfo -libdir scilla/bin/stdlib -gaslimit "  + gas_limit + " " + filename + " -jsonerrors"
    messages = cli(command)
    print("*Warnings & Err Messages*")
    return messages

@app.route("/debug", methods=["POST"])
def debug():
    # Only allow post requests
    if request.method == 'POST':

        # Read POST request data
        filename = str(request.values.to_dict(flat=False)['filename'][0])
        gas_limit = str(request.values.to_dict(flat=False)['gas_limit'][0])
        source = str(request.values.to_dict(flat=False)['source'][0])

        # Decode scilla source
        decoded_source = str(base64.b64decode(source)).encode().decode("unicode-escape")
        decoded_source = decoded_source.replace("b\'","",1)
        valid_source =  decoded_source[:len(decoded_source)-1]

        # Save scilla file to disk
        scilla_file(filename, valid_source)

        print("debugged {0} ".format(filename))

    message_dic = json.loads(str( messages(filename,  gas_limit) ))

    if 'errors' in message_dic: # Err handling for minning Error messages key
        pass
    else:
        message_dic['errors'] = []

    #print( str( messages(filename,  gas_limit) ))

    payload = {
        "filename": filename,
        "gas_limit": gas_limit,
        "cash_flow_analysis": message_dic['cashflow_tags'],
        "gas_usage": message_dic['gas_remaining'],
        "warnings": message_dic['warnings'],
        "error": message_dic['errors'],
        "type_info": message_dic['type_info']
    }

    data = jsonify(payload) # Convert data to json

    print(payload)

    return data

if __name__ == "__main__":
    app.run(debug=True)
