# -*- coding: utf-8 -*-
"""
Anjal Hussan, Latif Masud and Sarah Wigodsky
DATA 602 Advanced Programming
Final Project - Healthy Eating
"""
import bs4 
from urllib.request import Request, urlopen
import re #regular expressions
from pymongo import MongoClient
from prettytable import PrettyTable

#scrapes the names of restaurants on fastfoodnutrition.org 
def restaurant_name_scraping(healthyfood):  
    url = 'https://fastfoodnutrition.org/'
    hdr = {'User-Agent': 'Edge'}
#Mozilla/5.0 (Windows NT 10.0; <64-bit tags>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/<Chrome Rev> Safari/<WebKit Rev> Edge/<EdgeHTML Rev>.<Windows Build>
    req = Request(url,headers=hdr)
    page = urlopen(req)
    soup = bs4.BeautifulSoup(page, "html.parser")
    
    rest_scrape = soup.find_all("a", {"title": re.compile('Nutrition Facts')})
    
    #adds restaurant name and name to access website to mongodb collection called healthyfood
    for item in rest_scrape:
        if item.text == '':
            break
        #remove apostrophe and replace space with dash
        web_name = item.text.replace("'",'').replace(' ','-').lower()  
        if rest_name.find({'webname':web_name}).count()==0:
            post = {"name": item.text, "webname": web_name}
            rest_name.insert_one(post)         
        rest_name.replace_one({"name":"Panera"},
                              {"name":"Panera",
                              "webname":"panera-bread"})    

#scrapes the menu for each restaurant
def menu_scraping(rest_name,food):
    for restaurant in rest_name.find():
        r_name = restaurant['name']
        url = 'https://fastfoodnutrition.org/'+restaurant['webname']
        print(url)
        hdr = {'User-Agent': 'Edge'}
        req = Request(url,headers=hdr)
        page = urlopen(req)
        soup = bs4.BeautifulSoup(page, "html.parser")

#scrapes the categories and menu items
        menu_items= soup.find_all("a", {"title": re.compile('Nutrition Facts')})
        for item in menu_items:
            if rest_name.find({'name':item.text}).count()==0:
                print(item.text)
                if 'items' in item.text: #identify menu category
                    numitems = re.findall(r"\d+",item.text)
                    numitems = numitems[0]
                    category = item.text.strip(" items").strip(" "+numitems)                
                else:
                    menu_item = item.text
                    web_menuname = menu_item.replace(" &","").replace("%","").replace(",","").replace("/","").replace("'",'').replace(' ','-').lower()
                    if web_menuname[-1]=="-":
                        web_menuname = web_menuname[:-1]
                    #scraping calories
                    url_cal = 'https://fastfoodnutrition.org/'+restaurant['webname']+"/"+web_menuname+"#"
                    req = Request(url_cal,headers=hdr)
                    try:
                        page_cal = urlopen(req)
                        soup_cal = bs4.BeautifulSoup(page_cal, "html.parser")
                        calories = soup_cal.find_all("td", {"title": re.compile('Calories in')})
                        try:
                            calories = float(calories[0].text)
                    
                    #entering food information into Mongodb
                            post = {"name":r_name,
                                    "webname":restaurant['webname'],
                                    "category":category,
                                    "menu_item":menu_item,
                                    "calories":calories}
                            food.insert_one(post)  
                        except IndexError:
                            continue
                        except ValueError:
                            continue
                    except UnicodeEncodeError:
                        continue
                    
#prints table of food from restaurants
def print_food(food):
    table = PrettyTable(["Restaurant Name", "webname", "Category", "Menu Item", "Calories"]) 

    for item in food.find():
        table.add_row([item['name'],item['webname'],item['category'],item['menu_item'],item['calories']])
    print(table)
            

MONGO_URI = "mongodb://test:test@ds139929.mlab.com:39929/healthyfooddb"
client = MongoClient(MONGO_URI, connectTimeoutMS = 30000) 
db = client.get_database()
rest_name = db.rest_name
food = db.food

if food.count()==0:
    restaurant_name_scraping(rest_name) 
    menu_scraping(rest_name, food)
print_food(food)