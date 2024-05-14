# mongodump-python

## Description
Mongodump-python is a Python tool for performing MongoDB backups using the `mongodump` utility. This tool allows you to dump specific collections from your MongoDB database according to a specified number of days.

## Features
- Perform MongoDB backups using Python;
- Dump specific collections based on a specified number of days;
- Simple and easy-to-use Python script;

## Usage
1. **Clone the repository:**
    ```bash
    git clone https://github.com/tbernacchi/mongodump-python.git
    ```

2. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Edit the `script.py` file** to configure your MongoDB connection settings and specify the collections you want to backup.

4. **Run the `script.py` script:**
    ```bash
    python script.py
    ```

## Configuration
You can configure the tool by editing the configmap file. Here are the available options:

- `MONGODB_URI`: MongoDB connection URI.
- `DAYS`: Number of days for filtering collections to be backed up.
- `COLLECTIONS`: List of collections to be backed up.

## Example
To backup collections that have documents with a `date` field within the last 30 days:

```python
MONGODB_URI = "mongodb://localhost:27017/mydatabase"
DAYS = 30
COLLECTIONS = ["collection1", "collection2"]

