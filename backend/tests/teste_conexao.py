from pymongo import MongoClient
uri = "mongodb+srv://<db_username>:<db_password>@cluster.codigo.mongodb.net/"
client = MongoClient(uri)
try:
    client.admin.command("ping")
    print("Connected successfully")
    client.close()
except Exception as e:
    raise Exception(
        "The following error occurred: ", e)