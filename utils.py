import pymongo 

connection_string = 'mongodb+srv://dbuser:resubd@cluster0.oq7ov.mongodb.net/final_project?retryWrites=true&w=majority'

def get_db_handle():
 client = pymongo.MongoClient(connection_string)
 db = client['final_project']
 return db, client

# db, client = get_db_handle()

# for coll in db.list_collection_names():
#     print(coll)