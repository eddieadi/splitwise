# Splitwise-Flask-App

Splitwise-Flask-App is a Flask-based application for managing expenses and groups. Users can create accounts, add expenses, and track balances with friends in various groups.

## Table of Contents

- [Database Setup](#database-setup)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)

## Database Setup

### Create Database and Tables

Execute the following SQL commands to set up the required database tables:

```sql
CREATE DATABASE splitwise;

-- Table to store users
CREATE TABLE User (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    MobileNumber VARCHAR(255) NOT NULL
);

-- Table to store group-user relationships
CREATE TABLE GroupUser (
    GroupID INT,
    UserID INT,
    CreatedByUserID INT,
    PRIMARY KEY (GroupID, UserID)
);

-- Table to store expenses
CREATE TABLE Expense (
    ExpenseID INT PRIMARY KEY AUTO_INCREMENT,
    Description VARCHAR(200) NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    ExpenseTypeID INT NOT NULL,
    CreatedByUserID INT NOT NULL,
    GroupID INT,
    FOREIGN KEY (CreatedByUserID) REFERENCES User(UserID),
    FOREIGN KEY (GroupID) REFERENCES GroupUser(GroupID)
);

-- Table to store user-specific expenses
CREATE TABLE UserExpense (
    UserID INT,
    ExpenseID INT,
    Share DECIMAL(10, 2) NOT NULL,
    UserExpenseTypeID INT,
    PRIMARY KEY (UserID, ExpenseID),
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    FOREIGN KEY (ExpenseID) REFERENCES Expense(ExpenseID)
);

-- Table to store user-group relationships
CREATE TABLE UserGroup (
    UserID INT,
    GroupID INT,
    PRIMARY KEY (UserID, GroupID),
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    FOREIGN KEY (GroupID) REFERENCES GroupUser(GroupID)
);

-- Additional tables for status and types (you can customize these as needed)
CREATE TABLE UserStatus (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Value VARCHAR(50) NOT NULL
);

CREATE TABLE ExpenseType (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Value VARCHAR(50) NOT NULL
);

CREATE TABLE UserExpenseType (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Value VARCHAR(50) NOT NULL
);

Installation
Clone the repository to your local machine:
git clone https://github.com/eddieadi/splitwise.git
cd splitwise

Create a virtual environment and activate it:
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install the required dependencies:
pip install -r requirements.txt

Running the Application

Before running the application, ensure that your MySQL server is running, and update the database configuration in app.py with your MySQL credentials:
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'splitwise'


Now, run the Flask application:
python app.py
The application will be accessible at http://localhost:5000.

API Endpoints
/api/create_user: POST endpoint to create a new user.
/api/add_expense: POST endpoint to add a new expense.
/api/show_expenses/<user_id>: GET endpoint to retrieve expenses for a specific user.
/api/show_balances: GET endpoint to retrieve balances for everyone.
/api/calculate_expense: POST endpoint to calculate expenses based on different methods.
Explore the API and customize the application based on your needs!