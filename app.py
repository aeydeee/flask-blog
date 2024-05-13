from flask import Flask, render_template

# Create a Flask Instance
app = Flask(__name__)


# Create a route decorator
@app.route("/")
def index():
    first_name = "John"
    stuff = 'This is bold text'

    favorite_pizza = ['Pepperoni', 'Cheese', 'Mushrooms', 41]
    return render_template("index.html",
                           first_name=first_name,
                           stuff=stuff,
                           favorite_pizza=favorite_pizza)


@app.route("/user/<name>")
def greet(name):
    return render_template("user.html", username=name)


# Create a Custom Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Error handler for 500 (Internal Server Error)
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500
