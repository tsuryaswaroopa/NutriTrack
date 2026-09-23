# NutriTrack Pro

A smart web-based nutrition tracking application built using Flask, SQLite, AI, and Machine Learning.

NutriTrack helps users track their daily food intake, monitor calories and nutrients, set personalized nutrition goals, track weight progress, and predict future weight using Machine Learning.

---

## Features

### 🔐 User Authentication
- User registration
- User login
- Password validation
- Forgot password functionality
- Session-based authentication

### 🎯 Personalized Nutrition Goals
Users can enter their personal information such as:
- Age
- Gender
- Height
- Current weight
- Target weight
- Activity level

The application calculates:
- BMI
- BMR
- TDEE
- Daily calorie target
- Protein goal
- Water goal

### 🍎 Food Tracking
Users can:
- Add food entries
- Select meal type
- Enter food quantity
- Calculate calories
- Track protein
- Track carbohydrates
- Track fat
- Edit food entries
- Delete food entries

### 📊 Nutrition Dashboard
The dashboard provides a visual summary of daily nutrition including:
- Calories
- Protein
- Carbohydrates
- Fat
- Meal-wise nutrition
- Nutrition charts

### 🤖 AI Nutrition Chatbot
NutriTrack includes an AI-powered nutrition assistant.

The chatbot can:
- Answer nutrition-related questions
- Use the user's nutrition goals
- Access the user's daily food records
- Calculate remaining calories and protein
- Suggest meals
- Log food entries through chat
- Recommend foods from the NutriTrack food database

The chatbot is connected to an AI model through the OpenRouter API using the OpenAI Python SDK.

### 📈 Weight Progress Tracking
Users can record their monthly weight and monitor their progress.

The application displays:
- Weight history
- Starting weight
- Latest weight
- Weight change
- Weight progress graph

Users can also delete individual weight records.

### 🧠 ML Weight Prediction
NutriTrack uses Machine Learning to estimate future weight based on recorded weight history.

The prediction feature uses:

**Linear Regression**

It provides:
- Next month's predicted weight
- Weight prediction for 3 months from now
- Actual vs predicted weight graph

### 🎨 User Interface
- Responsive design
- Bootstrap components
- Font Awesome icons
- Custom CSS
- Nutrition-themed design
- Video background on Login and Register pages

---

## Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5.3.7
- Font Awesome 6.6.0
- Chart.js

### Backend
- Python
- Flask
- Jinja2

### Database
- SQLite

### Artificial Intelligence
- OpenRouter API
- OpenAI Python SDK

### Machine Learning
- Scikit-learn
- Linear Regression
- NumPy
- SciPy

### Development Tools
- Visual Studio Code
- Python Virtual Environment
- Git
- GitHub

---

## Project Structure

```text
FoodNutritionTracker/
│
├── static/
│   ├── css/
│   │   ├── chatbot.css
│   │   └── style.css
│   │
│   ├── images/
│   │   ├── broccoli.jpeg
│   │   ├── plate.png
│   │   └── veggies.png
│   │
│   ├── js/
│   │   └── chart.js
│   │
│   └── videos/
│
├── templates/
│   ├── about.html
│   ├── add_food.html
│   ├── chatbot.html
│   ├── dashboard.html
│   ├── edit_food.html
│   ├── forget_password.html
│   ├── goals.html
│   ├── index.html
│   ├── login.html
│   ├── plan_result.html
│   ├── planner.html
│   ├── predict_weight.html
│   ├── progress.html
│   └── register.html
│
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
└── README.md