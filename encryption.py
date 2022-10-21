from cryptography.fernet import Fernet
from datetime import datetime
from dotenv import load_dotenv
import crcmod
import six
import os
import base64
import sys
import json
from google.cloud import storage
from google.cloud import kms

load_dotenv()
project_id=os.environ["PROJECT_ID"]
location_id=os.environ["LOCATION_ID"]
key_ring_id=os.environ["KEY_RING_ID"]
key_id=os.environ["KEY_ID"]



def DecryptKMS(ciphertext):
    client = kms.KeyManagementServiceClient()
    key_name = client.crypto_key_path(project_id, location_id, key_ring_id, key_id)
    decrypt_response = client.decrypt(
        request={'name': key_name, 'ciphertext': ciphertext})
    return decrypt_response.plaintext

def EncryptKMS(plaintext):
    plaintext_bytes = plaintext.encode('utf-8')
    client = kms.KeyManagementServiceClient()
    key_name = client.crypto_key_path(project_id, location_id, key_ring_id, key_id)
    encrypt_response = client.encrypt(
      request={'name': key_name, 'plaintext': plaintext_bytes})
    return base64.b64encode(encrypt_response.ciphertext)

def ReadFromStorage(bucket_name, file):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file)
    return blob.download_as_bytes()


def WriteToStorage(bucket_name, file):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file)
    blob.upload_from_filename(file)


def Encrypt(key, bytes, out_file_name):
    f = Fernet(key)
    size = len(bytes)

    print("Input File Size: " + str(size))
    index = 0

    with open(out_file_name, "wb") as fout:
        while True:
            start=index*524288
            end=(index+1)*524288
            block = bytes[start:end]   #2^19
            if not block:
                break
            output = f.encrypt(block)
            index+=1
            fout.write(output)
    print("Encryption Completed")

def Decrypt(key, file_bytes, out_file_name):
    f = Fernet(key)
    with open(out_file_name, "wb") as fout:
        while True:
            block = file_bytes.read(699148)
            if not block:
                break
            outputd = f.decrypt(block)
            fout.write(outputd)

    file_out_stats = os.stat(out_file_name)
    print("Decryption Completed")
    print("Decrypted File Size: " + str(file_out_stats.st_size))

def CreateKey():
    from cryptography.fernet import Fernet
    print(str(EncryptKMS(str(Fernet.generate_key()))).replace('/', '\/'))



if __name__ == '__main__':
    globals()[sys.argv[1]]()
