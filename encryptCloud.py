from cryptography.fernet import Fernet
import ibm_boto3
from ibm_botocore.client import Config, ClientError

COS_ENDPOINT = "https://s3.eu-de.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
COS_INSTANCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/15f6dd4774d140888d8ec03dee3144e5:7999e5e0-9199-4382-859f-90763932fd17:bucket:cos.encrypt.test"
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

def load_key():
    """
    Loads the key from the current directory named `key.key`
    """
    return open("key.key", "rb").read()

def encrypt(filename, key):
    """
    Given a filename (str) and key (bytes), it encrypts the file and write it
    """
    f = Fernet(key)
    with open(filename, "rb") as file:
        file_data = file.read()
    # encrypt data
    encrypted_data = f.encrypt(file_data)
    # write the encrypted file
    with open(filename, "wb") as file:
        file.write(encrypted_data)

def create_text_file(bucket_name, item_name, file_text):

    print("Creating new item: {0}".format(item_name))
    try:
        cos.Object(bucket_name, item_name).put(
            Body=file_text
        )
        print("Item: {0} created!".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to create text file: {0}".format(e))

if __name__ == "__main__":
    # load the key
    key = load_key()
    # file name
    file = "data.csv"
    # encrypt it
    encrypt(file, key)
    #Send it to COS
    create_text_file("cos.encrypt.test","data.csv","data.csv")



