from django.http.response import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .database_functions import *
from bson import ObjectId
from django.views.generic import TemplateView

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

class overview(TemplateView):
    template_name = "overview.html"

    def get(self, request):
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
        return render(request, self.template_name, context)

class login(TemplateView):
    template_name = 'login.html'
    def get(self, request):
        if "username" in request.COOKIES:
            return HttpResponseRedirect('/dashboard')        
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        try:
            context = {}
            un = request.POST['username']
            pwd = request.POST['password']
            found = False
            if un == 'admin' and pwd == 'admin':
                found = True
                name =  'Admin'

            if found == False:
                context['status'] = 'Invalid Login Details' 
            else:
                res = HttpResponseRedirect('/dashboard')
                res.set_cookie('username', name)  
                return res
            return render(request, self.template_name, context)
        except:
            return HttpResponse('<h1>Something went wrong!</h1><p>Please check your internet connectivity!</p>')

class logout(TemplateView):
    def get(self,request):
        res = HttpResponseRedirect('/')
        res.delete_cookie('username')
        return res

class home(TemplateView):
    template_name = 'index.html'
    def return_bar_graph(self, x,y,xlabel,ylabel, graph_type=None):    
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

    def return_pie_graph(self, x,y,colors):    
        fig = plt.figure(figsize=(5,4))
        plt.pie(y, labels=x)

        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)

        data = imgdata.getvalue()
        return data

    def return_age_hist(self, x):    
        fig = plt.figure(figsize=(5,4))
        plt.hist(x)

        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)

        data = imgdata.getvalue()
        return data

    def get(self, request):
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

        context['reviews_bar_graph'] = self.return_bar_graph(['positive', 'negative'], [p,n], 'No. of Reviews', 'Review Type') #{{ graph|safe }}
        context['ratings_bar_graph'] = self.return_bar_graph(x, y, 'No. of Ratings', 'Rating','barh') #{{ graph|safe }}
        context['gender_pie_chart'] = self.return_pie_graph(gx, gy, ['#FF4747','#248AFD'])
        context['age_histogram'] = self.return_age_hist(ages)

        context['total_users'] = len(list(get_all_users()))
        context['total_restaurants'] = len(list(get_all_restaurants()))
        context['total_dishes'] = len(list(get_all_dishes()))
        context['total_reviews'] = len(list(get_all_reviews()))
        
        return render(request, self.template_name, context)

class add_user(TemplateView):
    context = {}
    template_name = 'add_user.html'
    def get(self, request):
        if "q" in request.GET:
            id = request.GET.get('q')
            user_data = user_table.find_one({'_id':ObjectId(id)})
            user_data.update({'id':id})
            self.context['user_data'] = user_data
            self.context['update'] ='update'
        return render(request, self.template_name, self.context)
    def post(self, request):
        name = request.POST['name']
        passw = request.POST['password']
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
            self.context['u_status'] = 'User Updated Successfully!'
        else:
            if insert_user(name, passw, gen, age, exp, addr):
                self.context['status'] = 'User Added Successfully!'
            else:
                self.context['status'] = "Couldn't add user, try again!"

        return render(request, 'add_user.html', self.context)

class all_users(TemplateView): 
    template_name = 'all_users.html'
    def get(self, request):
        context = {}
        users = get_all_users()
        all_users = []
        for user in users:
            usr = dict(user)
            usr.update({'id':user['_id']})
            all_users.append(usr)
        context['users'] = all_users
        return render(request, self.template_name, context)

class delete_user(TemplateView):
    def get(self,request, id):
        user_table.delete_one({'_id': ObjectId(id)})
        return HttpResponseRedirect('/all_users/')

class add_restaurant(TemplateView):
    context= {}
    template_name = 'add_restaurant.html'
    def get(self,request):
        if "q" in request.GET:
            id = request.GET.get('q')
            rest_data = rest_table.find_one({'_id':ObjectId(id)})
            rest_data.update({'id':id})
            self.context['restaurant'] = rest_data
            self.context['update'] ='update'
        return render(request, self.template_name , self.context)

    def post(self, request):
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
            self.context['u_status'] = 'Restaurant Updated Successfully!'
        else:
            if insert_restaurant(name, type, location):
                self.context['status'] = 'Restaurant Added Successfully!'
            else:
                self.context['status'] = "Couldn't add restaurant, try again!"
        return render(request, self.template_name , self.context)

class all_restaurants(TemplateView):
    template_name = 'all_restaurants.html'
    def get(self,request):
        context = {}
        restaurants = get_all_restaurants()
        all_rests = []
        for rest in restaurants:
            rst = dict(rest)
            rst.update({'id':rest['_id']})
            all_rests.append(rst)
        context['restaurants'] = all_rests
        return render(request, self.template_name, context)

class delete_rest(TemplateView):
    def get(self,request, id):
        rest_table.delete_one({'_id': ObjectId(id)})
        return HttpResponseRedirect('/all_restaurants/')

class add_dish(TemplateView):
    template_name = 'add_dish.html'
    context= {}
    def get(self,request):
        restaurants = get_all_restaurants()
        all_rests = []
        for rest in restaurants:
            rst = dict(rest)
            rst.update({'r_id':rest['_id']})
            all_rests.append(rst)
        self.context['restaurants'] = all_rests

        if "q" in request.GET:
            id = request.GET.get('q')
            dish_data = dish_table.find_one({'_id':ObjectId(id)})
            dish_data.update({'id':id})
            self.context['dish_data'] = dish_data
            self.context['update'] ='update'
        return render(request, self.template_name, self.context)

    def post(self, request):
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
            self.context['u_status'] = 'Dish Updated Successfully!'
        else:
            if insert_dish(name, ObjectId(restaurant), price):
                self.context['status'] = 'Dish Added Successfully!'
            else:
                self.context['status'] = "Couldn't add dish, try again!"

        return render(request, 'add_dish.html', self.context)

class all_dishes(TemplateView):
    def get(self,request):
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

class delete_dish(TemplateView):
    def get(self,request, id):
        dish_table.delete_one({'_id': ObjectId(id)})
        return HttpResponseRedirect('/all_dishes/')

class add_review(TemplateView):
    context= {}
    template_name = 'add_review.html'
    def prediction(self,text):
        converted_text = count_vectorizor_model.transform([text])  
        result = model.predict(converted_text)
        decoded_result = decoded_obj[result[0]]
        return {"class":result[0], "text":decoded_result}
    def get(self,request):
        restaurants = get_all_restaurants()
        all_rests = []

        for rest in restaurants:
            rst = dict(rest)
    
            rst.update({'r_id':rest['_id']})
            all_rests.append(rst)
        self.context['restaurants'] = all_rests
        
        users = get_all_users()
        all_users = []
        for user in users:
            usr = dict(user)
            usr.update({'uid':user['_id']})
            all_users.append(usr)
        self.context['users'] = all_users
        return render(request, self.template_name, self.context)

    def post(self, request):
        restaurant = request.POST['restaurant']
        username = request.POST['username']
        review = request.POST['review']
        data = self.prediction(review)
        if data['class'] == 0:
            review_class = 'negtive'
        elif data['class'] == 1:
            review_class = 'positive'

        insert_review(ObjectId(restaurant), ObjectId(username), review,review_class)
        self.context['status'] = data['text']
        return render(request, self.template_name, self.context)

class all_reviews(TemplateView):
    template_name = 'all_reviews.html'
    def get(self, request):
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
        return render(request, self.template_name, context)

class delete_review(TemplateView):
    def get(self,request, id):
        reviews_table.delete_one({'_id': ObjectId(id)})
        return HttpResponseRedirect('/all_reviews/')

class add_rating(TemplateView):
    template_name = 'add_rating.html'
    context= {}

    def get(self,request):
        restaurants = get_all_restaurants()
        all_rests = []

        for rest in restaurants:
            rst = dict(rest)
            rst.update({'r_id':rest['_id']})
            all_rests.append(rst)
        self.context['restaurants'] = all_rests
        
        users = get_all_users()
        all_users = []
        for user in users:
            usr = dict(user)
            usr.update({'uid':user['_id']})
            all_users.append(usr)
        self.context['users'] = all_users
        return render(request, self.template_name, self.context)

    def post(self, request):
        print("rating=", request.POST)
        restaurant = request.POST['restaurant']
        username = request.POST['username']
        rating = request.POST['rating']

        insert_rating(ObjectId(restaurant), ObjectId(username), rating)
        self.context['status'] = 'Thanks for your valuable rating!'
        return render(request, self.template_name, self.context)

class all_ratings(TemplateView):
    def get(self,request):
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

class delete_rating(TemplateView):
    def get(self, request, id):
        ratings_table.delete_one({'_id': ObjectId(id)})
        return HttpResponseRedirect('/all_ratings/')


class delete_dish_review(TemplateView):
    def get(self,request, id):
        dish_review.delete_one({'_id': ObjectId(id)})
        return HttpResponseRedirect('/all_dish_review/')

class all_dish_reviews(TemplateView):
    template_name = 'all_dish_review.html'
    def get(self, request):
        context = {}
        reviews = get_all_dish_reviews()
        allreviews = []
        for review in reviews:
            rvw = dict(review)
            try:
                 rvw['restaurant'] = rest_table.find_one({'_id':ObjectId(rvw['restaurant'])})['name']
            except:
                rvw['restaurant']='testing restaurant'
            try:
                rvw['user'] = user_table.find_one({'_id':review['user']})['name']
            except:
                rvw['user'] = 'test'
            try:
                rvw['dish']=dish_table.find_one({'_id':review['dish']})['name']
            except:
                rvw['dish']="testing dish"
            rvw.update({'id':rvw['_id']})
            allreviews.append(rvw)
        context['reviews'] = allreviews
        return render(request, self.template_name, context)

class add_dish_review(TemplateView):
    context= {}
    template_name = 'add_dish_review.html'
    def get(self,request):
        restaurants = get_all_restaurants()
        all_rests = []
        for rest in restaurants:
            rst = dict(rest)
            rst.update({'r_id':rest['_id']})
            all_rests.append(rst)
        self.context['restaurants'] = all_rests
        
        users = get_all_users()
        all_users = []
        for user in users:
            usr = dict(user)
            usr.update({'uid':user['_id']})
            all_users.append(usr)
        self.context['users'] = all_users
        all_dishes=[]
        dishes=get_all_dishes()
        for dish in dishes:
            ds = dict(dish)
            ds.update({'id':dish['_id']})
            all_dishes.append(ds)
        self.context["dishes"]=all_dishes
        return render(request, self.template_name, self.context)

    def post(self, request):
        restaurant = request.POST['restaurant']
        user = request.POST['user']
        msg = request.POST['msg']
        dish=request.POST["dish"]
        status=request.POST['status']
        insert_dish_review(ObjectId(restaurant),ObjectId(dish), ObjectId(user), msg, status)
        self.context['status'] = status
        return render(request, self.template_name, self.context)