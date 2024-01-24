from flask import Flask, jsonify,render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'splitwise'
 
mysql = MySQL(app)

@app.route('/')
def hello_world():
	return 'Hello World'

@app.route('/api/create_user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()

        # Extract data from JSON request
        name = data['name']
        email = data['email']
        mobile_number = data['mobile_number']

        # Create the user
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO User (name, email, mobile_number) VALUES (%s, %s, %s)",
            (name, email, mobile_number)
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    try:
        data = request.get_json()

        # Extract data from JSON request
        description = data['description']
        amount = float(data['amount'])
        expense_type_id = int(data['expense_type_id'])
        created_by_user_id = int(data['created_by_user_id'])
        group_id = int(data.get('group_id', None))  # Optional, if you have groups

        # Create the expense
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO Expense (Description, Amount, ExpenseTypeID, CreatedByUserID, GroupID) VALUES (%s, %s, %s, %s, %s)",
            (description, amount, expense_type_id, created_by_user_id, group_id)
        )
        mysql.connection.commit()
        cur.close()

        # Extract participants and their shares from JSON request
        participants = data['participants']
        for participant in participants:
            user_id = int(participant['user_id'])
            share = float(participant['share'])

            # Create user expense entry
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO UserExpense (UserID, ExpenseID, Share) VALUES (%s, %s, %s)",
                (user_id, cur.lastrowid, share)
            )
            mysql.connection.commit()
            cur.close()

        return jsonify({'message': 'Expense added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/show_expenses/<user_id>', methods=['GET'])
def show_expenses(user_id):
    try:
        # Retrieve expenses for a single user
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM Expense WHERE user_id = %s",
            (user_id,)
        )
        expenses = cur.fetchall()
        cur.close()

        return jsonify({'expenses': expenses}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/show_balances', methods=['GET'])
def show_balances():
    try:
        # Retrieve balances for everyone with non-zero balances
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT u.name, e.amount FROM User u INNER JOIN Expense e ON u.userId = e.user_id WHERE e.amount != 0"
        )
        balances = cur.fetchall()
        cur.close()

        return jsonify({'balances': balances}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@app.route('/api/calculate_expense', methods=['POST'])
def calculate_expense():
    try:
        data = request.get_json()

        # Extract data from JSON request
        payer_id = int(data['payer_id'])
        amount = float(data['amount'])
        participants = data['participants']
        expense_type = data['expense_type']  # 'EQUAL', 'EXACT', 'PERCENT'

        # Calculate expenses based on the expense type
        if expense_type == 'EQUAL':
            equal_expense(amount, payer_id, participants)
        elif expense_type == 'EXACT':
            exact_expense(amount, payer_id, participants)
        elif expense_type == 'PERCENT':
            percent_expense(amount, payer_id, participants)
        else:
            return jsonify({'error': 'Invalid expense type'}), 400

        return jsonify({'message': 'Expense calculated successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def equal_expense(amount, payer_id, participants):
    # Calculate equal expense
    share_per_person = amount / len(participants)
    
    # Update balances
    for participant_id in participants:
        if participant_id != payer_id:
            update_balances(participant_id, payer_id, share_per_person)

def exact_expense(amount, payer_id, participants):
    # Extract exact shares from participants
    shares = {int(participant['user_id']): float(participant['share']) for participant in participants}

    # Validate total shares equal to amount
    if sum(shares.values()) != amount:
        raise ValueError('Total shares do not equal the total amount')

    # Update balances
    for participant_id, share in shares.items():
        if participant_id != payer_id:
            update_balances(participant_id, payer_id, share)

def percent_expense(amount, payer_id, participants):
    # Extract percentage shares from participants
    percentages = {int(participant['user_id']): float(participant['percent']) for participant in participants}

    # Validate total percentage equal to 100
    if sum(percentages.values()) != 100:
        raise ValueError('Total percentage does not equal 100')

    # Calculate amount for each participant based on percentage
    shares = {participant_id: (amount * percentage / 100) for participant_id, percentage in percentages.items()}

    # Update balances
    for participant_id, share in shares.items():
        if participant_id != payer_id:
            update_balances(participant_id, payer_id, share)

def update_balances(user_id, payer_id, amount):
    # Update balances in the database
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE User SET balance = balance + %s WHERE userId = %s",
        (amount, user_id)
    )
    cur.execute(
        "UPDATE User SET balance = balance - %s WHERE userId = %s",
        (amount, payer_id)
    )
    mysql.connection.commit()
    cur.close()


# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application 
	# on the local development server.
	app.run()