import os
import gzip
from datetime import datetime, timedelta
from pymongo import MongoClient
import bson 
import json
import uuid
from google.cloud import storage

def get_date_days_ago_ms():
    # Calculates the timestamp x days ago in milliseconds.
    days = int(os.environ.get('DAYS')) # Days to keep the data.
    ninety_days_ago = datetime.now() - timedelta(days=days)
    date = int(ninety_days_ago.strftime("%s000")) 
    return date

# Get the number of days from the environment variable
days_value = os.environ.get('DAYS')
print(f"Number of days: {days_value}")

milliseconds = get_date_days_ago_ms()
print(f"Timestamp {days_value} in milliseconds:{milliseconds}")

# Connection details
mongo_user = "root"
mongo_pass = os.environ.get('MONGO_PASS')
host = os.environ.get('HOST')
port = 27017
replica_set = "rs0"
authSource = "admin"
mongo_db_pipeline = "pipelinecore"

connection_uri = f"mongodb://{mongo_user}:{mongo_pass}@{host}:{port}/?replicaSet={replica_set}&authSource={authSource}"
print(f"Connection URI: {connection_uri}")

print(f"Connection String: {connection_uri}")
print(f"Database Name: {mongo_db_pipeline}")

# Connect to MongoDB replica set
client = MongoClient(connection_uri)
db = client[mongo_db_pipeline]  

print(f"Connection successful on { mongo_db_pipeline }...")

# Get list of all collection names in the database
collection_names = db.list_collection_names()

# Collection auditing
collection_name     = "auditing"
query               = { "dateStart": {"$gte": milliseconds }} # Query to filter documents.
output_dir          = "/tmp/dump-mongo"

# Check if the output dir exists
if not os.path.exists(output_dir):
    # Create the directory
    os.makedirs(output_dir)
    print(f"Directory '{output_dir}' created successfully...")
else:
    print(f"Directory '{output_dir}' already exists, moving on...")

print(f"Query: {query}")

print("It was found %d documents from auditing" % db.auditing.count_documents({}))
print(
    "It was found %d documents from auditing using query %s"
    % (db.auditing.count_documents(query), json.dumps(query))
)

# Print message before dumping
print(f"Starting to dump metadata and collection data...")

# Define the number of days to keep the data
days = int(os.environ.get('DAYS'))# Days to keep the data.

for collection in collection_names:
    try:
        # Retrieve collection information, including the UUID
        collection_info = db.command('listCollections', filter={'name': collection})
        collection_uuid_binary = collection_info['cursor']['firstBatch'][0]['info']['uuid']
        collection_uuid = uuid.UUID(bytes=collection_uuid_binary)

        # Create a metadata dictionary
        metadata = {
            'indexes': [
                {
                    'v': {'$numberInt': '2'},
                    'key': {'_id': {'$numberInt': '1'}},
                    'name': '_id_'
                }
            ],
            'uuid': collection_uuid.hex,  # Use the hex representation of the UUID
            'collectionName': collection,
            'type': 'collection'
        }

        # Save metadata to a JSON file
        metadata_filename = f"{output_dir}/{collection}-metadata.json"
        with open(metadata_filename, "w") as metadata_file:
            json.dump(metadata, metadata_file)
        print(f"Metadata of collection {collection} saved to {metadata_filename} successfully...")
    
        # Dump the collection auditing data with query
        if collection  == collection_name:
            with gzip.open(f"{output_dir}/{collection_name}-{days}.bson.gz", "wb") as dump_file:
                for doc in db[collection].find({'dateStart': {"$gte": milliseconds}}):
                    dump_file.write(bson.BSON.encode(doc))  # Serialize each document to BSON
            continue
        # Dump all the collections data without query    
        with gzip.open(f"{output_dir}/{collection}.bson.gz", "wb") as dump_file:
            for doc in db[collection].find():
                dump_file.write(bson.BSON.encode(doc))  # Serialize each document to BSON
        print(f"Collection {collection} dumped to {output_dir}/{collection}.bson.gz successfully...")

    except Exception as e:
        print(f"Error retrieving metadata and dumping data for collection {collection_name}: {e}")

print("All metadata and collection data dumped successfully!")

# Google Cloud Storage bucket
client = storage.Client()
current_datetime = datetime.now()
timestamp = current_datetime.strftime("%Y_%m_%d__%H:%M")

project_name = os.environ.get("PROJECT_NAME")

# Define the destination bucket and folder names
destination_folder_name = "pipelinecore"
destination_bucket_name = f"{project_name}-mongo-backup"

# Iterate over the files in the output directory
for file in os.listdir(output_dir):
    file_path = os.path.join(output_dir, file)  # Get the full path of the file
    folder_name = os.path.basename(output_dir) # Get the folder name from the output directory
    destination_blob_folder = f"{destination_folder_name}/{timestamp}__{destination_folder_name}"
    destination_blob_path = f"{destination_blob_folder}/{file}"

    # Get the destination bucket
    bucket = client.get_bucket(destination_bucket_name)

    # Create a blob object in the destination bucket
    blob = bucket.blob(destination_blob_path)

    # Upload the file to the destination blob
    blob.upload_from_filename(file_path)

print(f"Uploading files to gs://{destination_bucket_name}/{destination_blob_folder}...")
print("All files uploaded successfully!")
