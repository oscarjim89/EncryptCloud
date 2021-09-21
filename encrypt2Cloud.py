from cryptography.fernet import Fernet
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from datetime import date, datetime
import time
import os, sys
import json
import base64

CONFIG_PATH="OKV2cloud.conf"
#Verify config Path location...
if(os.path.exists(CONFIG_PATH) == False):
    print("Error: Config path doesn't exist")
#Load JSON config file with parameters
with open(CONFIG_PATH, 'rb') as config_file:
    #config = json.loads(base64.b64decode(config_file.read()).decode('utf8'))
    config_p = json.loads(config_file.read())

cos = ibm_boto3.resource("s3",
    ibm_api_key_id=config_p['API_KEY'],
    ibm_service_instance_id=config_p['COS_INSTANCE_CRN'],
    config=Config(signature_version="oauth"),
    endpoint_url=config_p['COS_ENDPOINT'],
    auth_function=token_proxy()                     
)

def token_proxy():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    proxy = {
        "https": "http://10.113.10.13:8080"
    }
    params = {
        "apikey":config_p['API_KEY'],
        "response_type":"cloud_iam",
        "grant_type":"urn:ibm:params:oauth:grant-type:apikey"
    }
    response = requests.request('POST', url="https://iam.cloud.ibm.com/oidc/token", headers=headers, params=params, timeout=30, proxies=proxy)

    return response.json

#Loads the key from the current directory named `key.key`
def load_key(key):
    return open(key, "rb").read()

#Given a filename (str) and key (bytes), it encrypts the file and write it
def encrypt(filename, key):
    f = Fernet(key)
    with open(filename, "rb") as file:
        file_data = file.read()
    # encrypt data
    encrypted_data = f.encrypt(file_data)
    # write the encrypted file
    with open(filename, "wb") as file:
        file.write(encrypted_data)

def upload(bucket_name, item_name, file_text):
    
    print("Creating new item: {0}".format(item_name))
    try:
        cos.Object(bucket_name, item_name).put(
            Body=file_text
        )
        print("Item: {0} uploaded!".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to update text file: {0}".format(e))

if __name__ == "__main__":
    #Check the key path
    if(os.path.isdir(config_p['key_path']) == False):
        print("key path doesn't exist: "+os.path.realpath(config_p['key_path'])+" .The script will exit with error")
        sys.exit(1)
    if(os.path.isdir(config_p['data_path']) == False):
        print("data path doesn't exist: "+os.path.realpath(config_p['data_path'])+" .The script will exit with error")
        sys.exit(1)
    #Verify input syntax
    if(len(sys.argv) != 1):
        print("Wrong number of arguments. Format must be: python encryptOKV2Cloud.py")
        sys.exit(1)
    else:
        #if key file doesn't exist...
        if(os.path.isfile(config_p['key_name']) == False):
            print("Error: Key File doesn't exist. Generate a new one...")
            sys.exit(1)
        else:
            #Load key
            key=load_key(config_p['key_path']+config_p['key_name'])
            #Load files to encrypt
            files = os.listdir(config_p['data_path'])
            #Only encrypts files modified today
            
            for f in files:
                path_file = config_p['data_path']+f
                file_date = date.fromtimestamp(os.stat(path_file).st_mtime)
                today = date.today()
                if(today.day == file_date.day):
                    #Encrypting data
                    print("Encrypting file " + f)
                    encrypt(path_file, key)
                    #Uploading to the Cloud
                    print("uploading file " + path_file)
                    upload(config_p['BUCKET_NAME'],f,path_file)
                    #Verifying uploaded file
    
