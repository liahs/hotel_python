from django.http.response import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .database_functions import *
from bson import ObjectId

# Create your views here.
import matplotlib.pyplot as plt
from io import StringIO
import numpy as np
import pickle
import pandas as pd

cv_file = open('models/review_cv.pkl',"rb")
count_vectorizor_model = pickle.load(cv_file)

model = pickle.load(open("models/review_model_log.pkl", "rb"))
decoded_obj = {0:"Negative Feedback! We will try to improve it!",1:"Positive Feedback! Thanks for your support!"}

def return_bar_graph(x,y,xlabel,ylabel, graph_type=None):    
    fig = plt.figure(figsize=(5,4))
    if graph_type == None:
        plt.bar(x,y, color=['#f96868', 'green'])
    else:
        plt.barh(x,y)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # plt.legend(x, loc='upper right')
    
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return data

def return_pie_graph(x,y,colors):    
    fig = plt.figure(figsize=(5,4))
    plt.pie(y, labels=x)

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return data

def return_age_hist(x):    
    fig = plt.figure(figsize=(5,4))
    plt.hist(x)

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return data

def prediction(text):
    converted_text = count_vectorizor_model.transform([text])  
    result = model.predict(converted_text)
    decoded_result = decoded_obj[result[0]]
    return {"class":result[0], "text":decoded_result}

def overview(request):
    context = {}
    all_restaurants = get_all_restaurants()

    details = []
    for restaurant in all_restaurants:
        rest = dict(restaurant)
        rest_id = rest['_id']
        no_of_dishes = 0
        no_of_ratings = 0
        no_of_positive_reviews = 0
        no_of_negative_reviews = 0

        for dish in get_all_dishes():
            if dict(dish).get('restaurant') == rest_id:
                no_of_dishes += 1

        for rating in get_all_ratings():
            if dict(rating).get('restaurant') == rest_id:
                no_of_ratings += 1

        for review in get_all_reviews():
            if dict(review).get('restaurant') == rest_id:
                if dict(review).get('status') == 'positive':
                    no_of_positive_reviews += 1
                elif dict(review).get('status') == 'negative':
                    no_of_negative_reviews += 1

        rest['no_of_dishes'] = no_of_dishes
        rest['no_of_ratings'] = no_of_ratings
        rest['no_of_positive_reviews'] = no_of_positive_reviews
        rest['no_of_negative_reviews'] = no_of_negative_reviews
        details.append(rest)

    context['details'] = details
    return render(request, 'overview.html', context)

def login(request):
    try:
        if "username" in request.COOKIES:
            return HttpResponseRedirect('/dashboard')
        context = {}
        if request.method == "POST":
            found = False
            un = request.POST['username']
            pwd = request.POST['password']

            if un == 'admin' and pwd == 'admin':
                found = True
                name =  'Admin'

            if found == False:
                context['status'] = 'Invalid Login Details' 
            else:
                res = HttpResponseRedirect('/dashboard')
                res.set_cookie('username', name)  
                return res
    except:
        return HttpResponse('<h1>Something went wrong!</h1><p>Please check your internet connectivity!</p>')
    return render(request, 'login.html', context)

def logout(request):
    res = HttpResponseRedirect('/')
    res.delete_cookie('username')
    return res

def home(request):
    context = {}
    p,n=0,0
    for review in get_all_reviews():
        rv = dict(review)
        try:
            if rv['status'] == 'positive':
                p+=1
            elif rv['status'] == 'negative':
                n+=1
        except:pass
    
    ratings = []
    for rating in get_all_ratings():
        ratings.append(int(dict(rating)['rating']))

    data = pd.Series(ratings).value_counts()
    x = list(data.index) 
    y = pd.Series(ratings).value_counts().values
   
   
    genders = []
    ages = []
    for user in get_all_users():
        usr = dict(user)
        genders.append(usr['gender'].lower())
        ages.append(usr['age'])

    g_data = pd.Series(genders).value_counts()
    gx = list(g_data.index) 
    gy = g_data.values

    context['reviews_bar_graph'] = return_bar_graph(['positive', 'negative'], [p,n], 'No. of Reviews', 'Review Type') #{{ graph|safe }}
    context['ratings_bar_graph'] = return_bar_graph(x, y, 'No. of Ratings', 'Rating','barh') #{{ graph|safe }}
    context['gender_pie_chart'] = return_pie_graph(gx, gy, ['#FF4747','#248AFD'])
    context['age_histogram'] = return_age_hist(ages)

    context['total_users'] = len(list(get_all_users()))
    context['total_restaurants'] = len(list(get_all_restaurants()))
    context['total_dishes'] = len(list(get_all_dishes()))
    context['total_reviews'] = len(list(get_all_reviews()))
    
    return render(request, 'index.html', context)

def add_user(request):
    context = {}
    if "q" in request.GET:
        id = request.GET.get('q')
        user_data = user_table.find_one({'_id':ObjectId(id)})
        user_data.update({'id':id})
        context['user_data'] = user_data
        context['update'] ='update'

    if request.method == "POST":
        name = request.POST['name']
        passw = request.POST['password']
        email = request.POST['email']
        gen = request.POST['gender']
        age = request.POST['age']
        exp = request.POST['experience']
        addr = request.POST['address']
        if "update" in request.POST:
            id_to_update = request.POST['id']
            myquery = {'_id': ObjectId(id_to_update)}
            newvalues = {"$set":{
                "name":name, 
                "pass":passw,"gender":gen,"age":age, "exp":exp,"address":addr
            }}
            user_table.update_one(myquery, newvalues) 
            context['u_status'] = 'User Updated Successfully!'
        else:
            if insert_user(name, passw, gen, age, exp, addr):
                context['status'] = 'User Added Successfully!'
            else:
                context['status'] = "Couldn't add user, try again!"
    return render(request, 'add_user.html', context)

def all_users(request):
    context = {}
    users = get_all_users()
    all_users = []
    for user in users:
        usr = dict(user)
        usr.update({'id':user['_id']})
        all_users.append(usr)
    context['users'] = all_users
    return render(request, 'all_users.html', context)

def delete_user(request, id):
    user_table.delete_one({'_id': ObjectId(id)})
    return HttpResponseRedirect('/all_users/')

def add_restaurant(request):
    context= {}
    if "q" in request.GET:
        id = request.GET.get('q')
        rest_data = rest_table.find_one({'_id':ObjectId(id)})
        rest_data.update({'id':id})
        context['restaurant'] = rest_data
        context['update'] ='update'

    if request.method == "POST":
        name = request.POST['name']
        type = request.POST['type']
        location = request.POST['location']

        if "update" in request.POST:
            id_to_update = request.POST['id']
            myquery = {'_id': ObjectId(id_to_update)}
            newvalues = {"$set":{
                "name":name, 
                "type":type,
                "location":location,
            }}
            rest_table.update_one(myquery, newvalues) 
            context['u_status'] = 'Restaurant Updated Successfully!'
        else:
            if insert_restaurant(name, type, location):
                context['status'] = 'Restaurant Added Successfully!'
            else:
                context['status'] = "Couldn't add restaurant, try again!"

    return render(request, 'add_restaurant.html', context)

def all_restaurants(request):
    context = {}
    restaurants = get_all_restaurants()
    all_rests = []
    for rest in restaurants:
        rst = dict(rest)
        rst.update({'id':rest['_id']})
        all_rests.append(rst)
    context['restaurants'] = all_rests
    return render(request, 'all_restaurants.html', context)

def delete_rest(request, id):
    rest_table.delete_one({'_id': ObjectId(id)})
    return HttpResponseRedirect('/all_restaurants/')


def add_dish(request):
    context= {}
    restaurants = get_all_restaurants()
    all_rests = []
    for rest in restaurants:
        rst = dict(rest)
        rst.update({'r_id':rest['_id']})
        all_rests.append(rst)
    context['restaurants'] = all_rests

    if "q" in request.GET:
        id = request.GET.get('q')
        dish_data = dish_table.find_one({'_id':ObjectId(id)})
        dish_data.update({'id':id})
        context['dish_data'] = dish_data
        context['update'] ='update'

    if request.method == "POST":
        name = request.POST['name']
        restaurant = request.POST['restaurant']
        price = request.POST['price']

        if "update" in request.POST:
            id_to_update = request.POST['id']
            myquery = {'_id': ObjectId(id_to_update)}
            newvalues = {"$set":{
                "name":name, 
                "restaurant":ObjectId(restaurant),
                "price":price,
            }}
            dish_table.update_one(myquery, newvalues) 
            context['u_status'] = 'Dish Updated Successfully!'
        else:
            if insert_dish(name, ObjectId(restaurant), price):
                context['status'] = 'Dish Added Successfully!'
            else:
                context['status'] = "Couldn't add dish, try again!"

    return render(request, 'add_dish.html', context)

def all_dishes(request):
    context = {}
    dishes = get_all_dishes()
    all_dishes = []
    for dish in dishes:
        dsh = dict(dish)
        dsh['restaurant'] = rest_table.find_one({'_id':ObjectId(dsh['restaurant'])})['name']
        dsh.update({'id':dish['_id']})
        all_dishes.append(dsh)
    context['dishes'] = all_dishes
    return render(request, 'all_dishes.html', context)

def delete_dish(request, id):
    dish_table.delete_one({'_id': ObjectId(id)})
    return HttpResponseRedirect('/all_dishes/')

def add_review(request):
    context= {}
    restaurants = get_all_restaurants()
    all_rests = []

    for rest in restaurants:
        rst = dict(rest)
        rst.update({'r_id':rest['_id']})
        all_rests.append(rst)
    context['restaurants'] = all_rests
    
    users = get_all_users()
    all_users = []
    for user in users:
        usr = dict(user)
        usr.update({'uid':user['_id']})
        all_users.append(usr)
    context['users'] = all_users

    if request.method == "POST":
        restaurant = request.POST['restaurant']
        username = request.POST['username']
        review = request.POST['review']

        data = prediction(review)
        if data['class'] == 0:
            review_class = 'negtive'
        elif data['class'] == 1:
            review_class = 'positive'

        insert_review(ObjectId(restaurant), ObjectId(username), review,review_class)
        context['status'] = data['text']
    return render(request, 'add_review.html', context)

def all_reviews(request):
    context = {}
    reviews = get_all_reviews()
    allreviews = []
    for review in reviews:
        rvw = dict(review)
        rvw['restaurant'] = rest_table.find_one({'_id':ObjectId(rvw['restaurant'])})['name']
        try:
            rvw['username'] = user_table.find_one({'_id':review['user']})['name']
        except:
            rvw['username'] = 'test'
    
        rvw.update({'id':rvw['_id']})
        allreviews.append(rvw)
    context['reviews'] = allreviews
    return render(request, 'all_reviews.html', context)

def delete_review(request, id):
    reviews_table.delete_one({'_id': ObjectId(id)})
    return HttpResponseRedirect('/all_reviews/')

def add_rating(request):
    context= {}
    restaurants = get_all_restaurants()
    all_rests = []

    for rest in restaurants:
        rst = dict(rest)
        rst.update({'r_id':rest['_id']})
        all_rests.append(rst)
    context['restaurants'] = all_rests
    
    users = get_all_users()
    all_users = []
    for user in users:
        usr = dict(user)
        usr.update({'uid':user['_id']})
        all_users.append(usr)
    context['users'] = all_users

    if request.method == "POST":
        print("rating=", request.POST)
        restaurant = request.POST['restaurant']
        username = request.POST['username']
        rating = request.POST['rating']

        insert_rating(ObjectId(restaurant), ObjectId(username), rating)
        context['status'] = 'Thanks for your valuable rating!'
    return render(request, 'add_rating.html', context)


def all_ratings(request):
    context = {}
    ratings = get_all_ratings()
    allratings = []
    for rating in ratings:
        rat = dict(rating)
        rat['restaurant'] = rest_table.find_one({'_id':ObjectId(rat['restaurant'])})['name']
        try:
            rat['username'] = user_table.find_one({'_id':rat['user']})['name']
        except:
            rat['username'] = 'test'
    
        rat.update({'id':rat['_id']})
        allratings.append(rat)
    context['ratings'] = allratings
    return render(request, 'all_ratings.html', context)


def delete_rating(request, id):
    ratings_table.delete_one({'_id': ObjectId(id)})
    return HttpResponseRedirect('/all_ratings/')
