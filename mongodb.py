from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://longcule:Longcule1311@dic-db.szexbjy.mongodb.net/?retryWrites=true&w=majority&appName=dic-db"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Chọn database
db = client['db-dic']

# Chọn collection
collection = db['account']

def get_all_prod(collection_name):
    collection = db[collection_name]
    items = collection.find()

    data = []
    for item in items:
        item_dict = dict(item)
        item_dict['_id'] = str(item_dict['_id'])  # Convert ObjectId to string
        data.append(item_dict)

    return data


def add_prod_to_collection(item, collection_name):
    # Connect to the database and select the collection
    collection = db[collection_name]
    largest_id_item = collection.find_one(sort=[('id', -1)])
    

    item['id'] = largest_id_item['id'] + 1
    item_with_id_at_beginning = {'id': item['id']}
    item_with_id_at_beginning.update(item)
    collection.insert_one(item_with_id_at_beginning)
    # client.close()

def delete_item(item_id, collection_name):

    collection = db[collection_name]

    # Xác định câu truy vấn để xóa mục
    query = {"id": item_id}

    # Xóa mục khỏi collection
    result = collection.delete_one(query)

    # Kiểm tra xem mục có được xóa thành công không
    if result.deleted_count == 1:
        return "Mục đã được xóa thành công."
    else:
        return "Không tìm thấy mục hoặc không thể xóa."



def update_prod_by_id(item_id, update_fields, collection_name):
    # Connect to the database and select the collection
    collection = db[collection_name]

    # Update the fields of the item based on its ID
    collection.update_one({"id": item_id}, {"$set": update_fields})

    # Close the database connection
    # client.close()





def update_image(id, list_id_img, list_add_img, collection_name):
    # Connect to the database and select the collection
    collection = db[collection_name]
    # Retrieve the image IDs from the collection
    image_ids = []
    items = collection.find({"id": id})

    for item in items:
        if "image" in item:
            for image in item["image"]:
                if "id" in image:
                    image_id = image["id"]
                    if image_id not in list_id_img:
                        image_inf = {"id": image_id, "link": image['link']}
                        image_ids.append(image_inf)

    k = 20
    for item in list_add_img:
        image_inf = {"id": k, "link": item}
        image_ids.append(image_inf)
        k = k+1
    
    reindexed_image_ids = []
    for i, image in enumerate(image_ids):
        image['id'] = i
        reindexed_image_ids.append(image)
    
    
    # Close the database connection
    # client.close()
    return reindexed_image_ids

# lis = [0]

# list_add_img = []
# print(get_image_ids(56, lis, list_add_img  ,'product'))

def get_item_by_id(item_id, collection_name):
    collection = db[collection_name]
    item = collection.find_one({'id': item_id})

    if item:
        item_dict = dict(item)
        item_dict['_id'] = str(item_dict['_id'])  # Convert ObjectId to string
        return item_dict
    else:
        return []
    
def find_account_by_username_and_password(collection_name, username, password):
    collection = db[collection_name]
    account = collection.find_one({
        'user_name': username,
        'password': password
    })
    if account:
        item_dict = dict(account)
        item_dict['_id'] = str(item_dict['_id'])  # Convert ObjectId to string
        return item_dict
    else:
        return "Sai tên đăng nhập hoặc mật khẩu!"