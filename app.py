from flask import Flask, render_template, request, url_for
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField,DateField

app = Flask(__name__)
app.config["SECRET_KEY"]="include_a_strong_secret_key"
app.config["MONGO_URI"] = "mongodb+srv://ywei004:<password>@cluster0.6nx458r.mongodb.net/?retryWrites=true&w=majority"
mongo = PyMongo(app)

# access db
db = mongo.db.db
# access db.expenses
expenses = db.expenses

class Expenses(FlaskForm):
    pass
    # TO BE COMPLETED (please delete the word pass above)

def get_total_expenses(category):
    pass
    # TO BE COMPLETED (please delete the word pass above)


@app.route('/')
def index():
    my_expenses = mongo.db.expenses.find()
    total_cost=0
    for i in my_expenses:
        total_cost+=float(i["cost"])
    expensesByCategory = [
        ("example" , get_total_expenses("example"))]
    # expensesByCategory is a list of tuples
    # each tuple has two elements:
    ## a string containing the category label, for example, insurance
    ## the total cost of this category
    return render_template("index.html", expenses=total_cost, expensesByCategory=expensesByCategory)


@app.route('/addExpenses',methods=["GET","POST"])
def addExpenses():
    # INCLUDE THE FORM
    if request.method == "POST":
        # INSERT ONE DOCUMENT TO THE DATABASE
        # CONTAINING THE DATA LOGGED BY THE USER
        # REMEMBER THAT IT SHOULD BE A PYTHON DICTIONARY
        return render_template("expenseAdded.html")
    return render_template("addExpenses.html",form=expensesForm)

app.run()