from flask import Flask, render_template, request, url_for, session
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField,DateField
from wtforms.validators import NumberRange
import logging
import os
import json
import locale
import random
import requests

# read/write with files
def save_to_file(data,filename):
    with open(filename,'w') as write_file:
        json.dump(data,write_file,indent=2)

def read_from_file(filename):
    with open(filename,'r') as read_file:
        data = json.load(read_file)
    return data

# set the locale to your preferred currency format (e.g. USD)
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(16).hex()
app.config["MONGO_URI"] = "mongodb+srv://<username>:<password>@Cluster0.6nx458r.mongodb.net/?retryWrites=true&w=majority"
mongo = PyMongo(app).cx['currency']
#client = MongoClient(app.config["MONGO_URI"])
#db = client["db"]
#expenses = db["expenses"]

# expenditure categories
categories = ["Groceries","Restaurants","Rent","Electricity","Water","Gas","College","Party","Mortgage","Insurance"]

# generate random currencies to choose from
def generate_currency_choices():
    currency_list = read_from_file("currency_codes.json")
    countries = currency_list["currency"]
    country_numbers = random.sample(range(0,len(countries)),10)
    selected_countries = []
    for country in country_numbers:
        selected_countries.append(countries[country]["currency"])
    return selected_countries

class Expenses(FlaskForm):
    description = StringField("Description")
    category = SelectField("Category",choices=categories)
    cost = DecimalField("Cost",validators=[NumberRange(min=1)])
    currency = SelectField("Currency",choices=generate_currency_choices())
    date = DateField("Date")

def get_total_expenses(category):
    try:
        expenses = mongo.expenses.find({"category": category})
        total_cost = sum(expense["cost"] for expense in expenses)
        return total_cost
    except Exception as e:
        print(f"Error fetching expenses for category {category}: {e}")

# get currency exchange rates
def currency_exchange_rates(api_key):
    url = "https://api.apilayer.com/currency_data/live?apikey=".format(api_key)
    response = requests.get(url).json()
    results = response["quotes"]
    exchange_rates = {key[3:]: value for key, value in results.items()}
    # save currency exchange rates into session
    return exchange_rates

# grab the currency code by full name
def key_by_value(currency):
    currency_list = read_from_file("currency_codes.json")
    currency_list = currency_list["currency"]

    for item in currency_list:
        if item["currency"] == currency:
            return item["code"]
            
# currency exchange calculations
def exchange_currency(currency,amount):
    exchange_rates = session.get("exchange_rates",{})
    exchange_rate = float(exchange_rates[currency])
    return amount/exchange_rate


logging.basicConfig(level=logging.DEBUG)

with app.app_context():
    logging.debug(f'MongoDB URI: {app.config["MONGO_URI"]}')
    logging.debug(f'MongoDB client: {mongo.client}')
    logging.debug(f'MongoDB database: {mongo.db}')

@app.route('/')
def index():
    # loads things into session so we don't need to read stuff over and over again
    exchange_rates = currency_exchange_rates()
    session["exchange_rates"] = exchange_rates

    my_expenses = mongo.expenses.find()
    total_cost=0
    for i in my_expenses:
        total_cost+=float(i["cost"])
    expenses = locale.currency(total_cost, grouping=True)
    
    expensesByCategory = []
    for category in categories:
        if mongo.expenses.find_one({"category": category}) is not None:
            expensesByCategory.append((category,locale.currency(get_total_expenses(category), grouping=True)))
    # expensesByCategory is a list of tuples
    # each tuple has two elements:
    ## a string containing the category label, for example, insurance
    ## the total cost of this category
    print("total cost: {0}".format(total_cost))
    print("expenses by category: {0}".format(expensesByCategory))
    return render_template("index.html", expenses=expenses, expensesByCategory=expensesByCategory)


@app.route('/addExpenses',methods=["GET","POST"])
def addExpenses():
    # INCLUDE THE FORM
    expensesForm = Expenses(request.form)
    if request.method == "POST":
        # INSERT ONE DOCUMENT TO THE DATABASE
        # CONTAINING THE DATA LOGGED BY THE USER
        # REMEMBER THAT IT SHOULD BE A PYTHON DICTIONARY
        currency = request.form['currency']
        currency_key = key_by_value(currency)
        exchanged_currency = exchange_currency(currency_key,float(request.form['cost']))

        expense = {
            'description': request.form['description'],
            'category': request.form['category'],
            'cost': float(exchanged_currency),
            'date': request.form['date']
        }
        mongo.expenses.insert_one(expense)
        return render_template("expenseAdded.html")
    return render_template("addExpenses.html",form=expensesForm)

if __name__ == '__main__':
    app.run(port=8080,debug=True)

app.run()
