import os
from shell import shell
import json
import base64
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

# Command line interface
def cli(cmd):
    stream =  shell(cmd)

    stdout = stream.output(raw=True)
    err  = stream.errors(raw=True)

    output = ''

    if stdout:
       # print("output {0}".format(stdout))
        output = stdout

    else:
       # print("output {0}".format(err))
        output = err
    return output

# Reconstruct scilla file via REST
def scilla_file(filename, source):
    path = "{0}".format(filename)

    with open(path, 'w') as f:
        f.write(source)
    print("* {0} saved to disk.".format(filename))    
    return filename

# Warnings, Cashflow analysis & Error messages
def messages(filename, gas_limit):
    command = "scilla-checker -cf -typeinfo -libdir /home/ubuntu/scilla/src/stdlib -gaslimit "  + gas_limit + " " + filename + " -jsonerrors"
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

        try:
            # Decoding for non chunked base64 scilla files
            decoded_source = base64.b64decode(source).decode("unicode-escape") # Decode scilla source
            scilla_file(filename, decoded_source) # save scilla file to disk
        except:
            # Decoding for chunked base64 scilla files
            valid_source = source.replace('-','+') # strip out irlsafe placeholder
            full_chunk = b''
            single_chunk = valid_source + '==='
            decoded_chunk = base64.b64decode(single_chunk)

            full_chunk = full_chunk + decoded_chunk 

            decoded_source = full_chunk.decode("unicode-escape") # decode base64 scilla file as unicode
            scilla_file(filename, decoded_source) # save scilla file to disk
            

    print("debugged {0} ".format(filename))


    # get debug info as string
    message_dic = json.loads(str( messages(filename,  gas_limit) ))


    # insert placeholders for standard error messages from scilla-checker
    if 'errors' in message_dic:
        pass
    else:
        message_dic['errors'] = []

    if 'cashflow_tags' in message_dic:
        pass
    else:
        message_dic['cashflow_tags'] = []
    
    if 'type_info' in message_dic:
        pass
    else:
        message_dic['type_info'] = []

    if 'gas_remaining' in message_dic:
        pass
    else:
        message_dic['gas_remaining'] = gas_limit

    if 'filename' in message_dic: 
        pass
    else:
        message_dic['filename'] = filename

    if 'gas_limit' in message_dic:
        pass
    else:
        message_dic['gas_limit'] = gas_limit

    # print(message_dic)

    # construct payload
    payload = {
        "filename": filename,
        "gas_limit": gas_limit,
        "cash_flow_analysis": message_dic['cashflow_tags'],
        "gas_usage": message_dic['gas_remaining'],
        "warnings": message_dic['warnings'],
        "error": message_dic['errors'],
        "type_info": message_dic['type_info']
    }
    

    data = jsonify(payload)

    shell('rm -r *.scilla') 

    return data

if __name__ == "__main__":
    app.run(host='0.0.0.0')
