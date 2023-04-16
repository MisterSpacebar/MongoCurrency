from flask import Flask, render_template, request, url_for
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField,DateField
from wtforms.validators import NumberRange
import logging
import os
import locale

# set the locale to your preferred currency format (e.g. USD)
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(16).hex()
app.config["MONGO_URI"] = "mongodb+srv://ywei004:KGnwKTyAoJF9Y7OT@Cluster0.6nx458r.mongodb.net/?retryWrites=true&w=majority"
mongo = PyMongo(app).cx['db']
#client = MongoClient(app.config["MONGO_URI"])
#db = client["db"]
#expenses = db["expenses"]

categories = ["Groceries","Restaurants","Rent","Electricity","Water","Gas","College","Party","Mortgage","Insurance"]

class Expenses(FlaskForm):
    description = StringField("Description")
    category = SelectField("Category",choices=categories)
    cost = DecimalField("Cost",validators=[NumberRange(min=1)])
    date = DateField("Date")

def get_total_expenses(category):
    try:
        expenses = mongo.expenses.find({"category": category})
        total_cost = sum(expense["cost"] for expense in expenses)
        return total_cost
    except Exception as e:
        print(f"Error fetching expenses for category {category}: {e}")
    

logging.basicConfig(level=logging.DEBUG)

with app.app_context():
    logging.debug(f'MongoDB URI: {app.config["MONGO_URI"]}')
    logging.debug(f'MongoDB client: {mongo.client}')
    logging.debug(f'MongoDB database: {mongo.db}')

@app.route('/')
def index():

    my_expenses = mongo.expenses.find()
    total_cost=0
    for i in my_expenses:
        total_cost+=float(i["cost"])
    expenses = locale.currency(total_cost, grouping=True)
    
    expensesByCategory = []
    for category in categories:
        if mongo.db.expenses.find_one({"category": category}) is not None:
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
        expense = {
            'description': request.form['description'],
            'category': request.form['category'],
            'cost': float(request.form['cost']),
            'date': request.form['date']
        }
        mongo.expenses.insert_one(expense)
        return render_template("expenseAdded.html")
    return render_template("addExpenses.html",form=expensesForm)

if __name__ == '__main__':
    app.run(port=8080,debug=True)

app.run()