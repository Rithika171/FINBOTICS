FinBotics – Smart Money, Safe Future

About the Project

FinBotics is a smart personal finance and financial safety web application developed using Python and Django. It helps users manage their income, expenses, budgets, savings goals, and identify potentially fraudulent messages.

The main goal of FinBotics is to encourage better financial habits and improve awareness of online financial scams.

Features

1. User Authentication

- User registration and login
- Secure logout functionality
- Individual user accounts

2. Financial Dashboard

- View total income and expenses
- Track available balance
- View recent transactions
- Visualize financial data using charts

3. Transaction Management

- Add, edit, and delete transactions
- Organize income and expenses
- Search and filter transactions

4. Budget Planner

- Create monthly budgets
- Monitor category-wise spending
- Receive budget alerts at 75%, 90%, and 100% usage

5. Savings Goals

- Create personal savings goals
- Add money to goals
- Track savings progress
- Edit and delete goals

6. AI Financial Insights

- Analyze income and expenses
- Identify highest spending categories
- Compare monthly expenses
- Detect unusual spending patterns
- Calculate a financial health score

7. Scam Detection

- Analyze suspicious messages
- Identify potential phishing and scam indicators
- Calculate a risk score
- Classify messages as Low, Medium, or High risk
- Display warnings and safety recommendations
- Maintain scam detection history

8. Finance Chatbot

- Answer basic questions about income, expenses, balance, savings, and budgets
- Provide quick financial information through an interactive chatbot

9. Financial Reports

- Generate printable financial reports
- Save reports as PDF using the browser's print-to-PDF option

Technologies Used

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Django
- Database: SQLite
- Charts: Chart.js
- Python Libraries: python-dotenv and other Django dependencies

AI Implementation

FinBotics uses Python-based rule-driven logic for financial insights, chatbot responses, and scam detection.

The scam detector uses predefined keywords, regular expressions, risk scoring, and rule-based indicators to identify potentially suspicious messages.

Note: The current implementation does not use a trained machine learning model or an external generative AI API.

Installation and Setup

Prerequisites

- Python 3
- pip
- Visual Studio Code

Steps

1. Clone the repository:
   
   "git clone https://github.com/YOUR-USERNAME/FinBotics.git"

2. Open the project folder:
   
   "cd FinBotics"

3. Install dependencies:
   
   "pip install -r requirements.txt"

4. Create a ".env" file in the project root and add:
   
   "DJANGO_SECRET_KEY=your_secret_key"

5. Apply database migrations:
   
   "python manage.py migrate"

6. Start the development server:
   
   "python manage.py runserver"

7. Open the application in your browser:
   
   "http://127.0.0.1:8000/"

Security Notes

- Keep the ".env" file private.
- Never upload secret keys or sensitive credentials to GitHub.
- The local SQLite database is excluded from the repository.

Project Purpose

FinBotics aims to make personal financial management easier while helping users recognize potential online financial threats.

Project Name: FinBotics – Smart Money, Safe Future
Developed for: Arthaton 2026
