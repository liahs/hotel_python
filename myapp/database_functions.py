import pymongo 
from utils import get_db_handle

database, client = get_db_handle()
# 
user_table = database["User"]
rest_table = database["restaurants"]
dish_table = database["dishes"]
reviews_table = database["restreviews"]
ratings_table = database["restaurantratings"]
dish_review=database["dishreviews"]

# databse functions which we are going to use views classes
def insert_user(name, gender, age , address):
    mydict = { "name": name, "gender":gender, "age":age,"address":address }
    x = user_table.insert_one(mydict)
    if x:
        return True 
    else:
        return False

def get_all_users():
    cursor = user_table.find({})
    return cursor

def get_all_restaurants():
    cursor = rest_table.find({})
    return cursor

def insert_restaurant(name, type, location):
    mydict = { "name": name, "type":type, "location":location }
    x = rest_table.insert_one(mydict)
    if x:
        return True 
    else:
        return False

def get_all_dishes():
    cursor = dish_table.find({})
    return cursor

def insert_dish(name, restaurant, price):
    mydict = { "name": name, "restaurant":restaurant, "price":price }
    x = dish_table.insert_one(mydict)
    if x:
        return True 
    else:
        return False

def insert_review(restaurant, username, msz, status):
    mydict = { "restaurant": restaurant, "user":username, "msg":msz, "status":status }
    reviews_table.insert_one(mydict)

def insert_rating(restaurant, username, rating):
    mydict = { "restaurant": restaurant, "user":username, "rating":rating }
    ratings_table.insert_one(mydict)

def get_all_reviews():
    cursor  = reviews_table.find()
    return cursor

def get_all_dish_reviews():
    cursor=dish_review.find()
    return cursor

def insert_dish_review(restaurant,dish,user,msz,status):
    mydict = { "restaurant": restaurant,"dish":dish, "user":user, "msg":msz, "status":status }
    dish_review.insert_one(mydict) 

def get_all_ratings():
    cursor  = ratings_table.find()
    return cursor
    