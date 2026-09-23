from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from datetime import datetime
import os
import re
from openai import OpenAI
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.secret_key = "nutritrack_secret_key_2026"
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Nutrition values (per 100g)

nutrition_data = {
    
    # ---------- EGGS ----------
    "egg": {"calories":155,"protein":13,"carbs":1.1,"fat":11},
    "egg curry": {"calories":150,"protein":10,"carbs":4,"fat":10},
    "egg dosa": {"calories":210,"protein":10,"carbs":28,"fat":8},
    "egg biryani": {"calories":210,"protein":10,"carbs":24,"fat":8},
    "egg bhurji": {"calories":170,"protein":12,"carbs":3,"fat":12},
    "omelette": {"calories":190,"protein":13,"carbs":2,"fat":15},

    # ---------- RICE & GRAINS ----------
    "rice": {"calories":130,"protein":2.7,"carbs":28,"fat":0.3},
    "brown rice": {"calories":111,"protein":2.6,"carbs":23,"fat":0.9},
    "jeera rice": {"calories":150,"protein":3,"carbs":29,"fat":3},
    "tomato rice": {"calories":170,"protein":3.5,"carbs":30,"fat":5},
    "lemon rice": {"calories":190,"protein":3,"carbs":32,"fat":6},
    "curd rice": {"calories":140,"protein":4,"carbs":22,"fat":4},
    "fried rice": {"calories":180,"protein":5,"carbs":28,"fat":6},
    "pulihora": {"calories":190,"protein":3,"carbs":34,"fat":5},
    "khichdi": {"calories":140,"protein":5,"carbs":22,"fat":3},
    "veg pulao": {"calories":170,"protein":4,"carbs":28,"fat":5},
    "chicken pulao": {"calories":210,"protein":12,"carbs":22,"fat":8},
    "veg biryani": {"calories":180,"protein":4,"carbs":26,"fat":6},
    "chicken biryani": {"calories":220,"protein":12,"carbs":24,"fat":8},
    "mutton biryani": {"calories":260,"protein":15,"carbs":24,"fat":12},
    "millets": {"calories":119,"protein":3.5,"carbs":23,"fat":1},
    "oats": {"calories":389,"protein":17,"carbs":66,"fat":7},

    # ---------- BREAKFAST ----------
    "idli": {"calories":146,"protein":4.5,"carbs":30,"fat":0.5},
    "dosa": {"calories":168,"protein":4.5,"carbs":30,"fat":3.5},
    "masala dosa": {"calories":220,"protein":5,"carbs":34,"fat":8},
    "rava dosa": {"calories":190,"protein":5,"carbs":31,"fat":5},
    "pesarattu": {"calories":180,"protein":8,"carbs":24,"fat":5},
    "uttapam": {"calories":180,"protein":5,"carbs":30,"fat":4},
    "medu vada": {"calories":250,"protein":6,"carbs":30,"fat":12},
    "pongal": {"calories":160,"protein":4,"carbs":28,"fat":4},
    "poha": {"calories":130,"protein":2.6,"carbs":25,"fat":2},
    "upma": {"calories":209,"protein":5,"carbs":35,"fat":5},

    # ---------- ROTI ----------
    "chapati": {"calories":297,"protein":9,"carbs":55,"fat":3},
    "roti": {"calories":270,"protein":8,"carbs":52,"fat":3},
    "naan": {"calories":310,"protein":9,"carbs":58,"fat":6},
    "butter naan": {"calories":340,"protein":9,"carbs":58,"fat":9},
    "paratha": {"calories":320,"protein":7,"carbs":40,"fat":15},
    "puri": {"calories":300,"protein":6,"carbs":35,"fat":16},

    # ---------- DAL ----------
    "dal": {"calories":120,"protein":8,"carbs":18,"fat":2},
    "dal fry": {"calories":140,"protein":8,"carbs":18,"fat":4},
    "rajma curry": {"calories":130,"protein":8,"carbs":20,"fat":2},
    "chole": {"calories":160,"protein":9,"carbs":27,"fat":3},
    "moong dal": {"calories":105,"protein":7,"carbs":18,"fat":1},
    "sambar": {"calories":60,"protein":2.5,"carbs":8,"fat":2},
    "rasam": {"calories":30,"protein":1,"carbs":5,"fat":0.5},

    # ---------- CHICKEN ----------
    "chicken": {"calories":165,"protein":31,"carbs":0,"fat":3.6},
    "chicken curry": {"calories":180,"protein":20,"carbs":3,"fat":10},
    "chicken fry": {"calories":240,"protein":25,"carbs":4,"fat":14},
    "chicken 65": {"calories":290,"protein":22,"carbs":10,"fat":18},
    "butter chicken": {"calories":240,"protein":18,"carbs":6,"fat":16},
    "kadai chicken": {"calories":190,"protein":21,"carbs":5,"fat":10},
    "tandoori chicken": {"calories":170,"protein":27,"carbs":2,"fat":5},
    "chicken tikka": {"calories":190,"protein":27,"carbs":3,"fat":7},

    # ---------- FISH & SEAFOOD ----------
    "fish": {"calories":206,"protein":22,"carbs":0,"fat":12},
    "fish curry": {"calories":140,"protein":18,"carbs":3,"fat":6},
    "fish fry": {"calories":220,"protein":24,"carbs":4,"fat":11},
    "grilled fish": {"calories":170,"protein":26,"carbs":0,"fat":6},
    "prawns": {"calories":99,"protein":24,"carbs":0.2,"fat":0.3},
    "prawn curry": {"calories":140,"protein":22,"carbs":3,"fat":4},

    # ---------- MUTTON ----------
    "mutton curry": {"calories":250,"protein":18,"carbs":3,"fat":18},
    "mutton fry": {"calories":290,"protein":22,"carbs":2,"fat":22},

    # ---------- DAIRY ----------
    "milk": {"calories":61,"protein":3.2,"carbs":5,"fat":3.3},
    "curd": {"calories":98,"protein":11,"carbs":3.4,"fat":4.3},
    "paneer": {"calories":265,"protein":18,"carbs":1.2,"fat":21},
    "paneer butter masala": {"calories":280,"protein":12,"carbs":7,"fat":22},
    "palak paneer": {"calories":180,"protein":10,"carbs":6,"fat":12},
    "shahi paneer": {"calories":300,"protein":11,"carbs":8,"fat":25},
    "buttermilk": {"calories":40,"protein":3,"carbs":4,"fat":1},
    "lassi": {"calories":110,"protein":4,"carbs":15,"fat":4},

    # ---------- SOYA ----------
    "soya chunks": {"calories":345,"protein":52,"carbs":33,"fat":0.5},

    # ---------- VEGETABLES ----------
    "cucumber": {"calories":15,"protein":0.7,"carbs":3.6,"fat":0.1},
    "carrot": {"calories":41,"protein":0.9,"carbs":10,"fat":0.2},
    "tomato": {"calories":18,"protein":0.9,"carbs":3.9,"fat":0.2},
    "onion": {"calories":40,"protein":1.1,"carbs":9,"fat":0.1},
    "potato": {"calories":77,"protein":2,"carbs":17,"fat":0.1},
    "spinach": {"calories":23,"protein":2.9,"carbs":3.6,"fat":0.4},
    "mixed veg curry": {"calories":85,"protein":3,"carbs":12,"fat":3},
    "cabbage curry": {"calories":55,"protein":2,"carbs":8,"fat":2},
    "beans curry": {"calories":70,"protein":3,"carbs":9,"fat":2},
    "cauliflower curry": {"calories":60,"protein":2.5,"carbs":8,"fat":2},
    "beetroot curry": {"calories":65,"protein":2,"carbs":11,"fat":2},
    "drumstick curry": {"calories":70,"protein":3,"carbs":9,"fat":2},
    "lady finger fry": {"calories":90,"protein":2,"carbs":8,"fat":5},
    "brinjal curry": {"calories":75,"protein":2,"carbs":10,"fat":3},
    "bottle gourd curry": {"calories":40,"protein":1.5,"carbs":7,"fat":1},
    "sweet potato": {"calories":86,"protein":1.6,"carbs":20,"fat":0.1},

    # ---------- FRUITS ----------
    "apple": {"calories":52,"protein":0.3,"carbs":14,"fat":0.2},
    "banana": {"calories":89,"protein":1.1,"carbs":23,"fat":0.3},
    "orange": {"calories":47,"protein":0.9,"carbs":12,"fat":0.1},
    "mango": {"calories":60,"protein":0.8,"carbs":15,"fat":0.4},
    "watermelon": {"calories":30,"protein":0.6,"carbs":8,"fat":0.2},
    "papaya": {"calories":43,"protein":0.5,"carbs":11,"fat":0.3},
    "pineapple": {"calories":50,"protein":0.5,"carbs":13,"fat":0.1},
    "guava": {"calories":68,"protein":2.6,"carbs":14,"fat":1},
    "grapes": {"calories":69,"protein":0.7,"carbs":18,"fat":0.2},
    "muskmelon": {"calories":34,"protein":0.8,"carbs":8,"fat":0.2},

    # ---------- DRY FRUITS ----------
    "almonds": {"calories":579,"protein":21,"carbs":22,"fat":50},
    "peanuts": {"calories":567,"protein":26,"carbs":16,"fat":49},
    "cashews": {"calories":553,"protein":18,"carbs":30,"fat":44},
    "walnuts": {"calories":654,"protein":15,"carbs":14,"fat":65},
    "pistachios": {"calories":562,"protein":20,"carbs":28,"fat":45},
    "dates": {"calories":282,"protein":2.5,"carbs":75,"fat":0.4},
    "raisins": {"calories":299,"protein":3,"carbs":79,"fat":0.5},
    "chia seeds": {"calories":486,"protein":17,"carbs":42,"fat":31},

    # ---------- CHUTNEYS ----------
    "coconut chutney": {"calories":280,"protein":3,"carbs":10,"fat":27},
    "peanut chutney": {"calories":320,"protein":10,"carbs":12,"fat":28},
    "tomato chutney": {"calories":80,"protein":2,"carbs":8,"fat":4},

    # ---------- DRINKS ----------
    "tea": {"calories":35,"protein":1,"carbs":5,"fat":1},
    "coffee": {"calories":30,"protein":1,"carbs":4,"fat":1},
    "green tea": {"calories":2,"protein":0,"carbs":0,"fat":0},

    # ---------- MORE BREAKFAST ----------
    "vada": {"calories": 250, "protein": 6, "carbs": 30, "fat": 12},
    "mysore bonda": {"calories": 280, "protein": 6, "carbs": 32, "fat": 14},
    "appam": {"calories": 150, "protein": 3, "carbs": 30, "fat": 2},
    "ragi dosa": {"calories": 180, "protein": 5, "carbs": 30, "fat": 4},
    "ragi mudde": {"calories": 118, "protein": 2.5, "carbs": 25, "fat": 0.5},
    "ragi roti": {"calories": 220, "protein": 5, "carbs": 40, "fat": 5},
    "pesarattu upma": {"calories": 210, "protein": 8, "carbs": 30, "fat": 7},
    "bread": {"calories": 265, "protein": 9, "carbs": 49, "fat": 3},
    "brown bread": {"calories": 247, "protein": 13, "carbs": 41, "fat": 4},
    "bread omelette": {"calories": 230, "protein": 12, "carbs": 25, "fat": 10},

    # ---------- MORE RICE & GRAINS ----------
    "white rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
    "basmati rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
    "brown rice cooked": {"calories": 123, "protein": 2.7, "carbs": 25.6, "fat": 1},
    "rice noodles": {"calories": 109, "protein": 0.9, "carbs": 24, "fat": 0.2},
    "wheat ravva": {"calories": 342, "protein": 12, "carbs": 72, "fat": 1.5},
    "ragi flour": {"calories": 336, "protein": 7.3, "carbs": 72, "fat": 1.3},
    "jowar": {"calories": 329, "protein": 10.4, "carbs": 72, "fat": 3.1},
    "bajra": {"calories": 361, "protein": 11, "carbs": 67, "fat": 5},
    "quinoa": {"calories": 120, "protein": 4.4, "carbs": 21.3, "fat": 1.9},
    "corn": {"calories": 96, "protein": 3.4, "carbs": 21, "fat": 1.5},

    # ---------- MORE DAL & LEGUMES ----------
    "toor dal": {"calories": 343, "protein": 22, "carbs": 63, "fat": 1.7},
    "urad dal": {"calories": 341, "protein": 24, "carbs": 59, "fat": 1.4},
    "masoor dal": {"calories": 352, "protein": 25, "carbs": 63, "fat": 1.1},
    "chana dal": {"calories": 360, "protein": 22, "carbs": 60, "fat": 6},
    "green gram": {"calories": 347, "protein": 24, "carbs": 63, "fat": 1.2},
    "black chana": {"calories": 364, "protein": 19, "carbs": 61, "fat": 6},
    "white chana": {"calories": 364, "protein": 19, "carbs": 61, "fat": 6},
    "green peas": {"calories": 81, "protein": 5.4, "carbs": 14, "fat": 0.4},

    # ---------- MORE CHICKEN ----------
    "chicken breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    "chicken leg": {"calories": 209, "protein": 26, "carbs": 0, "fat": 11},
    "chicken soup": {"calories": 80, "protein": 8, "carbs": 5, "fat": 3},
    "chicken kebab": {"calories": 220, "protein": 27, "carbs": 5, "fat": 10},
    "chicken manchurian": {"calories": 220, "protein": 15, "carbs": 18, "fat": 10},
    "chicken noodles": {"calories": 190, "protein": 10, "carbs": 25, "fat": 6},
    "chicken shawarma": {"calories": 250, "protein": 18, "carbs": 25, "fat": 9},

    # ---------- MORE SEAFOOD ----------
    "prawn fry": {"calories": 180, "protein": 23, "carbs": 5, "fat": 7},
    "prawn biryani": {"calories": 220, "protein": 12, "carbs": 27, "fat": 7},
    "fish biryani": {"calories": 230, "protein": 13, "carbs": 25, "fat": 9},
    "crab": {"calories": 97, "protein": 19, "carbs": 0, "fat": 2},
    "crab curry": {"calories": 150, "protein": 18, "carbs": 4, "fat": 7},
    "sardines": {"calories": 208, "protein": 25, "carbs": 0, "fat": 11},
    "salmon": {"calories": 208, "protein": 20, "carbs": 0, "fat": 13},

    # ---------- MORE MUTTON ----------
    "mutton": {"calories": 294, "protein": 25, "carbs": 0, "fat": 21},
    "mutton biryani": {"calories": 260, "protein": 15, "carbs": 24, "fat": 12},
    "mutton soup": {"calories": 100, "protein": 10, "carbs": 2, "fat": 5},
    "mutton keema": {"calories": 250, "protein": 20, "carbs": 4, "fat": 17},

    # ---------- MORE VEGETABLES ----------
    "okra": {"calories": 33, "protein": 1.9, "carbs": 7.5, "fat": 0.2},
    "okra curry": {"calories": 80, "protein": 2, "carbs": 9, "fat": 4},
    "ridge gourd": {"calories": 20, "protein": 1.2, "carbs": 4.3, "fat": 0.2},
    "ridge gourd curry": {"calories": 55, "protein": 2, "carbs": 8, "fat": 2},
    "drumstick": {"calories": 64, "protein": 2.1, "carbs": 8.5, "fat": 1.4},
    "brinjal": {"calories": 25, "protein": 1, "carbs": 6, "fat": 0.2},
    "capsicum": {"calories": 31, "protein": 1, "carbs": 6, "fat": 0.3},
    "green beans": {"calories": 31, "protein": 1.8, "carbs": 7, "fat": 0.2},
    "bottle gourd": {"calories": 15, "protein": 0.6, "carbs": 3.4, "fat": 0.1},
    "pumpkin": {"calories": 26, "protein": 1, "carbs": 6.5, "fat": 0.1},
    "radish": {"calories": 16, "protein": 0.7, "carbs": 3.4, "fat": 0.1},
    "green chilli": {"calories": 40, "protein": 2, "carbs": 9, "fat": 0.2},

    # ---------- MORE FRUITS ----------
    "pomegranate": {"calories": 83, "protein": 1.7, "carbs": 18.7, "fat": 1.2},
    "kiwi": {"calories": 61, "protein": 1.1, "carbs": 15, "fat": 0.5},
    "pear": {"calories": 57, "protein": 0.4, "carbs": 15, "fat": 0.1},
    "strawberry": {"calories": 32, "protein": 0.7, "carbs": 7.7, "fat": 0.3},
    "dragon fruit": {"calories": 57, "protein": 1.2, "carbs": 13, "fat": 0.1},
    "chikoo": {"calories": 83, "protein": 0.4, "carbs": 20, "fat": 1.1},
    "custard apple": {"calories": 94, "protein": 2.1, "carbs": 23.6, "fat": 0.6},
    "fig": {"calories": 74, "protein": 0.8, "carbs": 19, "fat": 0.3},

    # ---------- SEEDS ----------
    "pumpkin seeds": {"calories": 559, "protein": 30, "carbs": 11, "fat": 49},
    "sunflower seeds": {"calories": 584, "protein": 21, "carbs": 20, "fat": 51},
    "flax seeds": {"calories": 534, "protein": 18, "carbs": 29, "fat": 42},
    "sesame seeds": {"calories": 573, "protein": 18, "carbs": 23, "fat": 50},
    "hemp seeds": {"calories": 553, "protein": 32, "carbs": 9, "fat": 49},

    # ---------- MORE DAIRY ----------
    "low fat curd": {"calories": 60, "protein": 5, "carbs": 7, "fat": 1.5},
    "greek yogurt": {"calories": 59, "protein": 10, "carbs": 3.6, "fat": 0.4},
    "cheese": {"calories": 402, "protein": 25, "carbs": 1.3, "fat": 33},
    "ghee": {"calories": 900, "protein": 0, "carbs": 0, "fat": 100},
    "butter": {"calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81},

    # ---------- SNACKS ----------
    "roasted chana": {"calories": 364, "protein": 19, "carbs": 61, "fat": 6},
    "makhana": {"calories": 347, "protein": 9.7, "carbs": 76, "fat": 0.1},
    "popcorn": {"calories": 375, "protein": 11, "carbs": 74, "fat": 4.5},
    "samosa": {"calories": 262, "protein": 5, "carbs": 32, "fat": 13},
    "pakora": {"calories": 280, "protein": 6, "carbs": 25, "fat": 17},
    "bhel puri": {"calories": 150, "protein": 4, "carbs": 25, "fat": 4},
    "pani puri": {"calories": 180, "protein": 4, "carbs": 30, "fat": 5},
    "sev puri": {"calories": 220, "protein": 5, "carbs": 30, "fat": 9},
    "sweet corn": {"calories": 96, "protein": 3.4, "carbs": 21, "fat": 1.5},

    # ---------- SWEETS ----------
    "gulab jamun": {"calories": 330, "protein": 4, "carbs": 48, "fat": 14},
    "jalebi": {"calories": 350, "protein": 2, "carbs": 75, "fat": 8},
    "laddu": {"calories": 420, "protein": 7, "carbs": 55, "fat": 20},
    "rasgulla": {"calories": 186, "protein": 4, "carbs": 38, "fat": 1},
    "kaju katli": {"calories": 480, "protein": 10, "carbs": 55, "fat": 25},
    "payasam": {"calories": 150, "protein": 3, "carbs": 22, "fat": 5},
    "rice kheer": {"calories": 160, "protein": 4, "carbs": 24, "fat": 5},
    "halwa": {"calories": 300, "protein": 3, "carbs": 45, "fat": 12},

    # ---------- ANDHRA / SOUTH INDIAN ----------
    "pulihora": {"calories": 190, "protein": 3, "carbs": 34, "fat": 5},
    "gongura pachadi": {"calories": 120, "protein": 3, "carbs": 8, "fat": 8},
    "avakaya": {"calories": 150, "protein": 2, "carbs": 12, "fat": 10},
    "pappu": {"calories": 120, "protein": 7, "carbs": 18, "fat": 2},
    "tomato pappu": {"calories": 125, "protein": 7, "carbs": 18, "fat": 3},
    "palakura pappu": {"calories": 115, "protein": 7, "carbs": 17, "fat": 2},
    "rasam rice": {"calories": 145, "protein": 3, "carbs": 27, "fat": 2},
    "curd rice": {"calories": 140, "protein": 4, "carbs": 22, "fat": 4},
    "kudumulu": {"calories": 180, "protein": 4, "carbs": 35, "fat": 2},
    "bobbatlu": {"calories": 300, "protein": 6, "carbs": 50, "fat": 9},

    # ---------- SOUPS ----------
    "vegetable soup": {"calories": 45, "protein": 2, "carbs": 8, "fat": 1},
    "tomato soup": {"calories": 50, "protein": 1.5, "carbs": 9, "fat": 1},
    "sweet corn soup": {"calories": 70, "protein": 2, "carbs": 12, "fat": 1},
    "egg soup": {"calories": 80, "protein": 6, "carbs": 4, "fat": 4},

    # ---------- BEVERAGES ----------
    "black coffee": {"calories": 2, "protein": 0.3, "carbs": 0, "fat": 0},
    "black tea": {"calories": 2, "protein": 0, "carbs": 0, "fat": 0},
    "coconut water": {"calories": 19, "protein": 0.7, "carbs": 3.7, "fat": 0.2},
    "lemon water": {"calories": 10, "protein": 0.2, "carbs": 3, "fat": 0},
    "orange juice": {"calories": 45, "protein": 0.7, "carbs": 10, "fat": 0.2},
    "mango juice": {"calories": 60, "protein": 0.5, "carbs": 14, "fat": 0.2},
    "sugarcane juice": {"calories": 74, "protein": 0.3, "carbs": 18, "fat": 0.1},

    # ---------- COMMON INGREDIENTS ----------
    "sugar": {"calories": 387, "protein": 0, "carbs": 100, "fat": 0},
    "jaggery": {"calories": 383, "protein": 0.4, "carbs": 98, "fat": 0.1},
    "coconut": {"calories": 354, "protein": 3.3, "carbs": 15, "fat": 33},
    "coconut milk": {"calories": 230, "protein": 2.3, "carbs": 5.5, "fat": 24},
    "corn flour": {"calories": 361, "protein": 8, "carbs": 76, "fat": 3.9},
    "besan": {"calories": 387, "protein": 22, "carbs": 58, "fat": 6.7},
    "rice flour": {"calories": 366, "protein": 6, "carbs": 80, "fat": 1.4},
    "wheat flour": {"calories": 340, "protein": 13, "carbs": 72, "fat": 2.5},
}
# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("nutrition.db")
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO users(fullname, email, password)
                VALUES(?,?,?)
            """, (fullname, email, password))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return "Email already exists!"

        conn.close()

        return redirect("/login")

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        session["email"] = email
        session["fullname"] = email.split("@")[0]

        # IMPORTANT:
        # After login user goes to Goals page first

        return redirect("/about")

    return render_template("login.html")
# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():

    if "email" not in session:
        return redirect("/login")

    return render_template(
        "about.html",
        fullname=session.get("fullname")
    )

@app.route("/plan_result", methods=["GET"])
def plan_result():
    if "email" not in session:
        return redirect("/login")

    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT goal, bmi, age, gender, height, current_weight, target_weight,
               activity_level, bmr, tdee, target_calories, protein_goal, water_goal
        FROM user_goals
        WHERE user_email=?
    """, (session["email"],))

    plan = cursor.fetchone()
    conn.close()

    if plan is None:
        return redirect("/planner")

    return render_template(
        "plan_result.html",
        fullname=session.get("fullname"),
        goal=plan[0],
        bmi=round(plan[1], 1),
        bmi_status="Normal",
        bmr=round(plan[8]),
        tdee=round(plan[9]),
        target_calories=round(plan[10]),
        protein_goal=round(plan[11]),
        water_goal=round(plan[12], 1)
    )

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "email" not in session:
        return redirect("/login")

    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()

    # -----------------------------------------------------
    # GET USER GOAL
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            target_calories,
            protein_goal,
            water_goal,
            goal
        FROM user_goals
        WHERE user_email=?
    """, (session["email"],))

    goal_data = cursor.fetchone()

    # Default values
    if goal_data:

        target_calories = goal_data[0] or 0
        target_protein = goal_data[1] or 0
        water_goal = goal_data[2] or 0
        goal = goal_data[3] or ""

    else:

        target_calories = 0
        target_protein = 0
        water_goal = 0
        goal = ""

    # -----------------------------------------------------
    # GET USER FOODS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            id,
            meal_type,
            food_name,
            quantity,
            calories,
            protein,
            carbs,
            fat
        FROM foods
        WHERE user_email=?
        ORDER BY id DESC
    """, (session["email"],))

    foods = cursor.fetchall()

    # -----------------------------------------------------
    # TOTAL NUTRITION
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            SUM(calories),
            SUM(protein),
            SUM(carbs),
            SUM(fat)
        FROM foods
        WHERE user_email=?
    """, (session["email"],))

    totals = cursor.fetchone()

    conn.close()

    # -----------------------------------------------------
    # CONVERT TOTALS
    # -----------------------------------------------------

    calories = round(totals[0] or 0, 2)
    protein = round(totals[1] or 0, 2)
    carbs = round(totals[2] or 0, 2)
    fat = round(totals[3] or 0, 2)

    # -----------------------------------------------------
    # REMAINING CALORIES
    # -----------------------------------------------------

    remaining = target_calories - calories

    if remaining < 0:
        remaining = 0

    # -----------------------------------------------------
    # CALORIE PROGRESS
    # -----------------------------------------------------

    if target_calories > 0:

        progress = (calories / target_calories) * 100

        if progress > 100:
            progress = 100

    else:

        progress = 0

    # -----------------------------------------------------
    # PROGRESS BAR COLOR
    # -----------------------------------------------------

    if progress < 50:

        progress_color = "bg-success"

    elif progress < 80:

        progress_color = "bg-warning"

    else:

        progress_color = "bg-danger"

    # -----------------------------------------------------
    # SEND DATA TO DASHBOARD
    # -----------------------------------------------------

    return render_template(
        "dashboard.html",

        foods=foods,

        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,

        totals=(calories, protein, carbs, fat),

        fullname=session.get("fullname"),

        goal=goal,

        target_calories=round(target_calories),
        target_protein=round(target_protein),
        water_goal=round(water_goal, 1),

        remaining=round(remaining),

        progress=round(progress),

        progress_color=progress_color
    )


# =========================================================
# ADD FOOD
# =========================================================

@app.route("/add_food", methods=["GET", "POST"])
def add_food():

    if "email" not in session:
        return redirect("/login")

    if request.method == "POST":

        meal_type = request.form["meal_type"]

        food_name = request.form["food_name"].strip().lower()

        quantity = float(request.form["quantity"])

        # Check food
        if food_name not in nutrition_data:

            return "Food not found in database!"

        food = nutrition_data[food_name]

        # Calculate nutrition according to quantity

        calories = round(
            food["calories"] * quantity / 100,
            2
        )

        protein = round(
            food["protein"] * quantity / 100,
            2
        )

        carbs = round(
            food["carbs"] * quantity / 100,
            2
        )

        fat = round(
            food["fat"] * quantity / 100,
            2
        )

        conn = sqlite3.connect("nutrition.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO foods
            (
                user_email,
                meal_type,
                food_name,
                quantity,
                calories,
                protein,
                carbs,
                fat
            )
            VALUES(?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)
        """,
        (
            session["email"],
            meal_type,
            food_name.title(),
            quantity,
            calories,
            protein,
            carbs,
            fat
        ))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_food.html")


# =========================================================
# EDIT FOOD
# =========================================================

@app.route("/edit_food/<int:id>", methods=["GET", "POST"])
def edit_food(id):

    if "email" not in session:
        return redirect("/login")

    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        meal_type = request.form["meal_type"]

        quantity = float(request.form["quantity"])

        # Get food name from database

        cursor.execute("""
            SELECT food_name
            FROM foods
            WHERE id=? AND user_email=?
        """, (id, session["email"]))

        result = cursor.fetchone()

        if result is None:

            conn.close()

            return "Food Not Found"

        # IMPORTANT:
        # Food was stored using .title()
        # So convert it back to lowercase

        food_name = result[0].strip().lower()

        if food_name not in nutrition_data:

            conn.close()

            return "Food nutrition data not found!"

        food = nutrition_data[food_name]

        calories = round(
            food["calories"] * quantity / 100,
            2
        )

        protein = round(
            food["protein"] * quantity / 100,
            2
        )

        carbs = round(
            food["carbs"] * quantity / 100,
            2
        )

        fat = round(
            food["fat"] * quantity / 100,
            2
        )

        cursor.execute("""
            UPDATE foods
            SET
                meal_type=?,
                quantity=?,
                calories=?,
                protein=?,
                carbs=?,
                fat=?
            WHERE id=? AND user_email=?
        """,
        (
            meal_type,
            quantity,
            calories,
            protein,
            carbs,
            fat,
            id,
            session["email"]
        ))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            id,
            meal_type,
            food_name,
            quantity
        FROM foods
        WHERE id=? AND user_email=?
    """, (id, session["email"]))

    food = cursor.fetchone()

    conn.close()

    if food is None:

        return "Food Not Found"

    return render_template(
        "edit_food.html",
        food=food
    )


# =========================================================
# UPDATE FOOD
# =========================================================

@app.route("/update_food/<int:id>", methods=["POST"])
def update_food(id):

    if "email" not in session:
        return redirect("/login")

    meal_type = request.form["meal_type"]

    food_name = request.form["food_name"].strip().lower()

    quantity = float(request.form["quantity"])

    if food_name not in nutrition_data:

        return "Food not found!"

    food = nutrition_data[food_name]

    calories = round(
        food["calories"] * quantity / 100,
        2
    )

    protein = round(
        food["protein"] * quantity / 100,
        2
    )

    carbs = round(
        food["carbs"] * quantity / 100,
        2
    )

    fat = round(
        food["fat"] * quantity / 100,
        2
    )

    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE foods
    SET
        meal_type=?,
        food_name=?,
        quantity=?,
        calories=?,
        protein=?,
        carbs=?,
        fat=?,
        created_at=CURRENT_TIMESTAMP
    WHERE id=? AND user_email=?
""",
(
    meal_type,
    food_name.title(),
    quantity,
    calories,
    protein,
    carbs,
    fat,
    id,
    session["email"]
))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# =========================================================
# DELETE FOOD
# =========================================================

@app.route("/delete_food/<int:id>")
def delete_food(id):

    if "email" not in session:
        return redirect("/login")

    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM foods
        WHERE id=? AND user_email=?
    """,
    (
        id,
        session["email"]
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# =========================================================
# GOALS
# =========================================================

@app.route("/goals")
def goals():

    if "email" not in session:
        return redirect("/login")

    return render_template(
        "goals.html",
        fullname=session.get("fullname")
    )


# =========================================================
# SET GOAL
# =========================================================

@app.route("/set_goal/<goal>")
def set_goal(goal):

    if "email" not in session:
        return redirect("/login")

    # Allowed goals

    allowed_goals = [
        "weight_loss",
        "fat_loss",
        "weight_gain",
        "muscle_gain",
        "maintenance"
    ]

    if goal not in allowed_goals:

        return "Invalid goal!"

    session["goal"] = goal

    return redirect("/planner")


# =========================================================
# PLANNER
# =========================================================

@app.route("/planner")
def planner():

    if "email" not in session:
        return redirect("/login")

    goal = session.get("goal")

    if not goal:

        return redirect("/goals")

    return render_template(
        "planner.html",

        fullname=session.get("fullname"),

        goal=goal
    )


# =========================================================
# CALCULATE PERSONALIZED PLAN
# =========================================================

@app.route("/calculate_plan", methods=["POST"])
def calculate_plan():

    if "email" not in session:
        return redirect("/login")

    # -----------------------------------------------------
    # GET FORM DATA
    # -----------------------------------------------------

    age = int(request.form["age"])

    gender = request.form["gender"]

    height = float(request.form["height"])

    current_weight = float(
        request.form["current_weight"]
    )

    target_weight = float(
        request.form["target_weight"]
    )

    activity = request.form["activity"]

    goal = request.form["goal"]

    # -----------------------------------------------------
    # BMI
    # -----------------------------------------------------

    bmi = current_weight / (
        (height / 100) ** 2
    )

    if bmi < 18.5:

        bmi_status = "Underweight"

    elif bmi < 25:

        bmi_status = "Normal"

    elif bmi < 30:

        bmi_status = "Overweight"

    else:

        bmi_status = "Obese"

    # -----------------------------------------------------
    # BMR
    # Mifflin-St Jeor equation
    # -----------------------------------------------------

    if gender == "Male":

        bmr = (
            10 * current_weight
            + 6.25 * height
            - 5 * age
            + 5
        )

    else:

        bmr = (
            10 * current_weight
            + 6.25 * height
            - 5 * age
            - 161
        )

    # -----------------------------------------------------
    # ACTIVITY FACTOR
    # -----------------------------------------------------

    activity_factor = {

        "Sedentary": 1.2,

        "Light": 1.375,

        "Moderate": 1.55,

        "Active": 1.725

    }

    # Check activity

    if activity not in activity_factor:

        return "Invalid activity level!"

    # -----------------------------------------------------
    # TDEE
    # -----------------------------------------------------

    tdee = bmr * activity_factor[activity]

    # -----------------------------------------------------
    # TARGET CALORIES BASED ON GOAL
    # -----------------------------------------------------

    if goal == "weight_loss":

        target_calories = tdee - 500

    elif goal == "fat_loss":

        target_calories = tdee - 300

    elif goal == "weight_gain":

        target_calories = tdee + 400

    elif goal == "muscle_gain":

        target_calories = tdee + 250

    elif goal == "maintenance":

        target_calories = tdee

    else:

        target_calories = tdee

    # Prevent extremely low calorie target

    if target_calories < 1200:

        target_calories = 1200

    # -----------------------------------------------------
    # PROTEIN GOAL
    # -----------------------------------------------------

    if goal in ["weight_loss", "fat_loss"]:

        protein_goal = current_weight * 1.8

    elif goal == "muscle_gain":

        protein_goal = current_weight * 2.0

    elif goal == "weight_gain":

        protein_goal = current_weight * 1.6

    else:

        protein_goal = current_weight * 1.2

    # -----------------------------------------------------
    # WATER GOAL
    # -----------------------------------------------------

    water_goal = current_weight * 35 / 1000

    # -----------------------------------------------------
    # SAVE PLAN TO DATABASE
    # -----------------------------------------------------

    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO user_goals
        (
            user_email,
            goal,
            age,
            gender,
            height,
            current_weight,
            target_weight,
            activity_level,
            bmi,
            bmr,
            tdee,
            target_calories,
            protein_goal,
            water_goal
        )
        VALUES
        (
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?
        )
    """,
    (
        session["email"],

        goal,

        age,

        gender,

        height,

        current_weight,

        target_weight,

        activity,

        bmi,

        bmr,

        tdee,

        target_calories,

        protein_goal,

        water_goal
    ))

    conn.commit()
    conn.close()

    # -----------------------------------------------------
    # SAVE GOAL IN SESSION
    # -----------------------------------------------------

    session["goal"] = goal

    # -----------------------------------------------------
    # SHOW RESULT
    # -----------------------------------------------------

    return render_template(
        "plan_result.html",

        fullname=session.get("fullname"),

        goal=goal,

        bmi=round(bmi, 1),

        bmi_status=bmi_status,

        bmr=round(bmr),

        tdee=round(tdee),

        target_calories=round(target_calories),

        protein_goal=round(protein_goal),

        water_goal=round(water_goal, 1)
    )
# =========================================================
# PROGRESS TRACKING
# =========================================================

@app.route("/progress", methods=["GET", "POST"])
def progress():

    if "email" not in session:
        return redirect("/login")

    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()

    # Create progress table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weight_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            month TEXT NOT NULL,
            weight REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_email, month)
        )
    """)

    # Save / update monthly weight
    if request.method == "POST":

        month = request.form["month"]
        weight = float(request.form["weight"])

        cursor.execute("""
            INSERT INTO weight_progress
            (user_email, month, weight)
            VALUES (?, ?, ?)
            ON CONFLICT(user_email, month)
            DO UPDATE SET weight=excluded.weight
        """, (
            session["email"],
            month,
            weight
        ))

        conn.commit()

    # Get user's weight history
    cursor.execute("""
        SELECT month, weight
        FROM weight_progress
        WHERE user_email=?
        ORDER BY month ASC
    """, (session["email"],))

    records = cursor.fetchall()

    conn.close()

    months = [record[0] for record in records]
    weights = [record[1] for record in records]

    # Weight summary
    if weights:

        starting_weight = weights[0]
        latest_weight = weights[-1]

        weight_change = round(
            latest_weight - starting_weight,
            1
        )

    else:

        starting_weight = 0
        latest_weight = 0
        weight_change = 0

    return render_template(
        "progress.html",

        records=records,
        months=months,
        weights=weights,

        starting_weight=starting_weight,
        latest_weight=latest_weight,
        weight_change=weight_change,

        fullname=session.get("fullname")
    )

# -----------------------------------------
# CHATBOT
# -----------------------------------------
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data.get("message", "").strip()
    

    if not user_message:
        return jsonify({
            "reply": "Please enter a message."
        })

    try:
    

        # Get logged-in user's email
        user_email = session.get("email")

        # -----------------------------------------
        # CHATBOT FOOD LOGGING
        # -----------------------------------------

        log_match = re.search(
            r"(?:log|add)\s+(\d+(?:\.\d+)?)\s*g\s+(.+?)\s+for\s+(breakfast|lunch|dinner|snack)",
            user_message.lower()
        )

        if log_match:
            quantity = float(log_match.group(1))
            food_name = log_match.group(2).strip()
            meal_type = log_match.group(3).title()

            if food_name not in nutrition_data:
                return jsonify({
                    "reply": f"Sorry, {food_name} is not available in the NutriTrack food database."
                })

            food = nutrition_data[food_name]

            calories = round(food["calories"] * quantity / 100, 2)
            protein = round(food["protein"] * quantity / 100, 2)
            carbs = round(food["carbs"] * quantity / 100, 2)
            fat = round(food["fat"] * quantity / 100, 2)

            conn = sqlite3.connect("nutrition.db")
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO foods
                (
                    user_email,
                    meal_type,
                    food_name,
                    quantity,
                    calories,
                    protein,
                    carbs,
                    fat,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                session["email"],
                meal_type,
                food_name.title(),
                quantity,
                calories,
                protein,
                carbs,
                fat
            ))

            conn.commit()
            conn.close()

            return jsonify({
                "reply": (
                    f"✅ Added {quantity:g} g of {food_name.title()} "
                    f"to {meal_type}.\n\n"
                    f"Calories: {calories} kcal\n"
                    f"Protein: {protein} g\n"
                    f"Carbs: {carbs} g\n"
                    f"Fat: {fat} g"
                )
            })

        # -----------------------------------------
        # USER GOAL INFORMATION
        # -----------------------------------------

        goal_info = "No nutrition goal information available."

        target_calories = 0
        protein_goal = 0

        # -----------------------------------------
        # TODAY'S FOOD INFORMATION
        # -----------------------------------------

        food_info = "No food entries recorded today."

        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0

        meal_totals = {}

        if user_email:

            conn = sqlite3.connect("nutrition.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get user's nutrition goal
            cursor.execute("""
                SELECT *
                FROM user_goals
                WHERE user_email = ?
            """, (user_email,))

            goal = cursor.fetchone()

            if goal:

                target_calories = float(goal["target_calories"] or 0)
                protein_goal = float(goal["protein_goal"] or 0)

                goal_info = f"""
User Nutrition Information:

Goal: {goal["goal"]}
Age: {goal["age"]}
Gender: {goal["gender"]}
Height: {goal["height"]} cm
Current Weight: {goal["current_weight"]} kg
Target Weight: {goal["target_weight"]} kg
Activity Level: {goal["activity_level"]}
BMI: {goal["bmi"]}
BMR: {goal["bmr"]} kcal
TDEE: {goal["tdee"]} kcal
Daily Calorie Target: {target_calories} kcal
Daily Protein Goal: {protein_goal} g
Daily Water Goal: {goal["water_goal"]} L
"""

            # Get today's food entries
            today = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("""
                SELECT meal_type, food_name, quantity,
                       calories, protein, carbs, fat
                FROM foods
                WHERE user_email = ?
                AND DATE(created_at) = ?
                ORDER BY id
            """, (user_email, today))

            foods = cursor.fetchall()
            print("TODAY:", today)
            cursor.execute("""
            SELECT id, user_email, meal_type, food_name, quantity, created_at
            FROM foods
            WHERE user_email = ?
            ORDER BY id DESC
            """, (user_email,))
            all_foods = cursor.fetchall()
            print("ALL USER FOODS:", [dict(food) for food in all_foods])

            conn.close()

            if foods:

                food_lines = []

                for food in foods:
                    total_calories += float(food["calories"] or 0)
                    total_protein += float(food["protein"] or 0)
                    total_carbs += float(food["carbs"] or 0)
                    total_fat += float(food["fat"] or 0)

                    meal = food["meal_type"]

                    if meal not in meal_totals:
                        meal_totals[meal] = {
                            "calories": 0,
                            "protein": 0,
                            "carbs": 0,
                            "fat": 0
                            }
                        meal_totals[meal]["calories"] += float(food["calories"] or 0)
                        meal_totals[meal]["protein"] += float(food["protein"] or 0)
                        meal_totals[meal]["carbs"] += float(food["carbs"] or 0)
                        meal_totals[meal]["fat"] += float(food["fat"] or 0)

                        food_lines.append(
                        f"- {food['meal_type']}: "
                        f"{food['food_name']} "
                        f"({food['quantity']} g) | "
                        f"{food['calories']} kcal | "
                        f"Protein: {food['protein']} g | "
                        f"Carbs: {food['carbs']} g | "
                        f"Fat: {food['fat']} g"
                    )

                food_info = """
Today's Food Entries:

""" + "\n".join(food_lines)

        # -----------------------------------------
        # CALCULATE REMAINING NUTRITION
        # -----------------------------------------

        remaining_calories = max(
            target_calories - total_calories,
            0
        )

        remaining_protein = max(
            protein_goal - total_protein,
            0
        )
        meal_summary = "Meal-wise Nutrition:\n"

        for meal, totals in meal_totals.items():
            meal_summary += (
                f"- {meal}: "
                f"{round(totals['calories'], 2)} kcal | "
                f"Protein: {round(totals['protein'], 2)} g | "
                f"Carbs: {round(totals['carbs'], 2)} g | "
                f"Fat: {round(totals['fat'], 2)} g\n"
            )
        nutrition_summary = f"""
Today's Nutrition Summary:

Calories consumed: {round(total_calories, 2)} kcal
Daily calorie target: {round(target_calories, 2)} kcal
Calories remaining: {round(remaining_calories, 2)} kcal

Protein consumed: {round(total_protein, 2)} g
Daily protein goal: {round(protein_goal, 2)} g
Protein remaining: {round(remaining_protein, 2)} g

Carbs consumed: {round(total_carbs, 2)} g
Fat consumed: {round(total_fat, 2)} g
"""

        # -----------------------------------------
        # SEND INFORMATION TO AI
        # -----------------------------------------
        # -----------------------------------------
# SEND INFORMATION TO AI
# -----------------------------------------

        available_foods = "\n".join(
            f"- {name}: {info['calories']} kcal, "
            f"Protein {info['protein']} g, "
            f"Carbs {info['carbs']} g, "
            f"Fat {info['fat']} g per 100 g"
            for name, info in nutrition_data.items()
        )

        response = client.chat.completions.create(

            model="openrouter/free",

            messages=[
                {
                    "role": "system",
                    "content": (
    "You are NutriTrack AI, a friendly nutrition assistant. "
    "IMPORTANT: When recommending foods, use ONLY foods that appear in the "
    "NutriTrack Food Database below. Never invent, substitute, or recommend "
    "foods outside this database, and never invent nutrition values.\n"
    "When the user asks what to eat, suggest practical meals using foods "
    "from the NutriTrack Food Database. Include the food name, quantity in grams, "
    "approximate calories, and protein for each item, followed by the meal total. "
    "Always consider the user's selected goal when giving nutrition advice. "
    "Adapt meal suggestions and guidance to that goal.\n\n"
    "Consider the user's remaining calories and protein when making suggestions.\n\n"
    "Nutrition values below are per 100 g as used by this app.\n\n"
    "NutriTrack Food Database:\n"
    + available_foods
    + "\n\n"
    + goal_info
    + "\n\n"
    + food_info
    + "\n\n"
    + meal_summary
    + "\n"
    + nutrition_summary
)
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]

        )

        print("AI RESPONSE:", response)
        reply = response.choices[0].message.content

        return jsonify({
            "reply": reply
        })

    except Exception as e:

        print("OpenRouter Error:", e)

        return jsonify({
            "reply": "Sorry, I couldn't connect to the AI right now."
        })

    # =========================================================
# CHATBOT ADD FOOD
# =========================================================

@app.route("/chat_add_food", methods=["POST"])
def chat_add_food():

    if "email" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        })

    data = request.get_json()

    food_name = data.get("food_name", "").strip().lower()
    meal_type = data.get("meal_type", "").strip()
    quantity = float(data.get("quantity", 0))

    if food_name not in nutrition_data:
        return jsonify({
            "success": False,
            "message": "Food not found in NutriTrack database."
        })

    if quantity <= 0:
        return jsonify({
            "success": False,
            "message": "Quantity must be greater than 0."
        })

    food = nutrition_data[food_name]

    calories = round(food["calories"] * quantity / 100, 2)
    protein = round(food["protein"] * quantity / 100, 2)
    carbs = round(food["carbs"] * quantity / 100, 2)
    fat = round(food["fat"] * quantity / 100, 2)

    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO foods
        (
            user_email,
            meal_type,
            food_name,
            quantity,
            calories,
            protein,
            carbs,
            fat,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        session["email"],
        meal_type,
        food_name.title(),
        quantity,
        calories,
        protein,
        carbs,
        fat
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"{quantity} g of {food_name.title()} added to {meal_type}.",
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat
    })
# =========================================================
# PREDICT WEIGHT
# =========================================================

@app.route("/predict_weight")
def predict_weight():

    if "email" not in session:
        return redirect("/login")

    conn = sqlite3.connect("nutrition.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT month, weight
        FROM weight_progress
        WHERE user_email = ?
        ORDER BY id
    """, (session["email"],))

    progress = cursor.fetchall()

    conn.close()

    # Prepare ML data
    month_numbers = []
    weights = []

    for index, item in enumerate(progress, start=1):
        month_numbers.append([index])
        weights.append(float(item["weight"]))

    predictions = None

    # Train model only when enough data is available
    if len(weights) >= 2:

        model = LinearRegression()

        model.fit(month_numbers, weights)

        next_month = len(weights) + 1

        predictions = {
            "next_month": round(
                model.predict([[next_month]])[0], 2
            ),
            "three_months": round(
                model.predict([[next_month + 2]])[0], 2
            )
        }

    return render_template(
        "predict_weight.html",
        progress=progress,
        predictions=predictions
    )
# =========================================================
# DELETE WEIGHT PROGRESS
# =========================================================

@app.route("/delete_progress/<month>", methods=["POST"])
def delete_progress(month):

    if "email" not in session:
        return redirect("/login")

    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM weight_progress
        WHERE user_email = ?
        AND month = ?
    """, (
        session["email"],
        month
    ))

    conn.commit()
    conn.close()

    return redirect("/progress")
# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)