import base64
import os
import encryption
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, request
import json

load_dotenv()
encrypted_key=os.environ["ENCRYPTED_KEY"]
destination_bucket=os.environ["DESTINATION_BUCKET"]

app = Flask(__name__)

@app.route("/", methods=["POST"])
def index():
    envelope = request.get_json()
    print(envelope)
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    
    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        message = base64.b64decode(pubsub_message["data"])

    file = json.loads(message)
    read_key_start = datetime.now()
    key=encryption.DecryptKMS(base64.b64decode(encrypted_key))
    read_key_end = datetime.now()
    read_key_time = read_key_end - read_key_start
    print("Rad Key millisecconds: " + str(read_key_time))

    read_file_start = datetime.now()
    bytes = encryption.ReadFromStorage(file["bucket"], file["name"])
    read_file_end = datetime.now()
    read_file_time = read_file_end - read_file_start
    print("Rad File millisecconds: " + str(read_file_time))

    encrypt_start = datetime.now()
    encryption.Encrypt(key,bytes,file["name"])
    encrypt_end = datetime.now()
    encrypt_time = encrypt_end - encrypt_start
    print("Encrypt millisecconds: " + str(encrypt_time))

    write_file_start = datetime.now()
    encryption.WriteToStorage(destination_bucket, file["name"])
    write_file_end = datetime.now()
    write_file_time = write_file_end - write_file_start
    print("Write File millisecconds: " + str(write_file_time))
    
    
    os.remove(file["name"])
    return ("", 204)

if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="127.0.0.1", port=PORT, debug=True)