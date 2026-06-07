from flask import Flask, render_template, request, redirect, url_for
from pony.orm import *
from models import *
import builtins
# Kreiranje Flask aplikacije
app = Flask(__name__)


@app.route("/")
@db_session
def home():
    foods = select(f for f in Food).order_by(desc(Food.date))[:]

    grouped_foods = {}

    for food in foods:
        if food.date not in grouped_foods:
            grouped_foods[food.date] = []

        grouped_foods[food.date].append(food)

    daily_goal = 2500

    return render_template(
        "index.html",
        grouped_foods=grouped_foods,
        daily_goal=daily_goal
    )
# Dodavanje nove hrane
@app.route("/add", methods=["GET", "POST"])
@db_session
def add_food():
    if request.method == "POST":
        name = request.form["name"]
        calories = int(request.form["calories"])
        date = request.form["date"]

        if calories <= 0:
            return redirect(url_for("add_food"))

        Food(
            name=name,
            calories=calories,
            date=date
        )

        return redirect(url_for("home"))

    return render_template("add_food.html")


# Brisanje postojećeg unosa hrane
@app.route("/delete/<int:id>", methods=["POST"])
@db_session
def delete_food(id):
    food = Food.get(id=id)

    if food:
        food.delete()

    return redirect(url_for("home"))


# Uređivanje postojećeg unosa
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@db_session
def edit_food(id):
    food = Food.get(id=id)

    if not food:
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form["name"]
        calories = int(request.form["calories"])
        date = request.form["date"]

        if calories <= 0:
            return redirect(url_for("edit_food", id=id))

        food.name = name
        food.calories = calories
        food.date = date

        return redirect(url_for("home"))

    return render_template("edit_food.html", food=food)


# Pretraživanje unosa po datumu
@app.route("/search", methods=["GET", "POST"])
@db_session
def search_food():
    foods = []
    selected_date = ""

    if request.method == "POST":
        selected_date = request.form["date"]
        foods = select(f for f in Food if f.date == selected_date)[:]

    return render_template(
        "search.html",
        foods=foods,
        selected_date=selected_date
    )


# Prikaz osnovne statistike kalorija
@app.route("/statistics", methods=["GET", "POST"])
@db_session
def statistics():
    goal = 2500
    selected_date = ""

    if request.method == "POST":
        goal = int(request.form.get("goal", 2500))

        if goal <= 0:
            goal = 2500

        selected_date = request.form.get("selected_date", "")

    if selected_date:
        foods = select(f for f in Food if f.date == selected_date)[:]
    else:
        foods = select(f for f in Food)[:]

    calories_by_date = {}

    for food in foods:
        if food.date not in calories_by_date:
            calories_by_date[food.date] = 0

        calories_by_date[food.date] += food.calories

    dates = list(calories_by_date.keys())
    calories = list(calories_by_date.values())

    total_calories = builtins.sum(calories)
    number_of_entries = len(foods)

    if number_of_entries > 0:
        average_calories = round(total_calories / number_of_entries, 2)
    else:
        average_calories = 0

    progress = min((total_calories / goal) * 100, 100)

    return render_template(
        "statistics.html",
        total_calories=total_calories,
        number_of_entries=number_of_entries,
        average_calories=average_calories,
        progress=progress,
        goal=goal,
        dates=dates,
        calories=calories,
        selected_date=selected_date
    )

# Pokretanje aplikacije
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)