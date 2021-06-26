from cryptography.fernet import Fernet
import sys, os
import json
import base64

CONFIG_PATH="OKV2cloud.conf"

#Generates a key and save it into a file
def write_key(key_name):
    key = Fernet.generate_key()
    with open(key_name, "wb") as key_file:
        key_file.write(key)

if __name__ == "__main__":
    #Load JSON config file with parameters
    with open(CONFIG_PATH, 'rb') as config_file:
	    #config = json.loads(base64.b64decode(config_file.read()).decode('utf8'))
        config = json.loads(config_file.read())
    #Check the path
    if(os.path.isdir(config['key_path']) == False):
        print("Object does not exist in specified path: "+os.path.realpath(config['key_path'])+" .The script will exit with error")
        sys.exit(1)
    #Generate new key
    write_key(config['key_name'])
    print("Output key: " + config['key_path'] + config['key_name'])