from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from decimal import Decimal

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

#MYSQL connection
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "bank_application"
app.config["MYSQL_PORT"] = 3307
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)


# Admin or User Selection Page
@app.route('/')
def admin_or_user():
    return render_template('Admin_or_User.html')

# <----------------------------------------------------------------------------------------------------------------------------------------------->


# Admin Authentication Route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to Admin DB
        con = mysql.connection.cursor()
        sql = "SELECT * FROM admin WHERE username = %s AND password = %s"
        con.execute(sql, (username, password))
        admin = con.fetchone()

        if admin:
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('Error_page_admin.html', message="Invalid Admin credentials")
    return render_template('Admin.html')


# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' in session:
        return render_template('Admin_dashboard.html', admin=session['admin'])
    return redirect(url_for('admin_login'))


# create user route
@app.route('/create-user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email_id = request.form['email']
        address = request.form['address']
        phone_no = request.form['phone']
        proof_type = request.form['proof_type']
        proof_id = request.form['proof_id']
        account_type = request.form['account_type']
        occupation = request.form['occupation']
        dob = request.form['dob']
        nationality = request.form['nationality']
        savings_amount = request.form['savings_amount']
        password = request.form['password']

        con = mysql.connection.cursor()

        # Check if phone number or password already exists
        con.execute("SELECT * FROM user WHERE ph_no = %s OR email_id = %s", [phone_no, email_id])
        existing_user = con.fetchone()

        if existing_user:
            # Flash error message if phone number or password already exists
            flash("Phone number or password already exists. Please enter new ones.")
            return redirect(url_for('create_user'))  # Redirect back to the form to enter new details
        else:
            # Proceed with user creation
            sql = """INSERT INTO user 
                     (first_name, last_name, email_id, address, ph_no, proof_type, proof_id, account_type, occupation, dob, nationality, savings_amount, password) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            con.execute(sql, [first_name, last_name, email_id, address, phone_no, proof_type, proof_id, account_type, occupation, dob, nationality, savings_amount, password])
            mysql.connection.commit()
            con.close()

            return redirect(url_for('view_users'))  # Redirect to the login page
    return render_template("New_account.html")


# Route for updating account details
@app.route('/update-user', methods=['GET', 'POST'])
def update_account():
    if request.method == 'POST':
        account_number = request.form['account_number']
        password = request.form['password']

        # Check if the account number and password exist
        con = mysql.connection.cursor()
        con.execute("SELECT * FROM user WHERE account_number = %s AND password = %s", (account_number, password))
        user = con.fetchone()

        if user:
            # Redirect to update_account.html with the user's current details
            return render_template('Update_account.html', user=user)
        else:
            # Flash error message if account number or password is incorrect
            flash("Account number or password is incorrect.")
            return redirect(url_for('update_account'))

    return render_template("Update_login.html")  # Render the form for entering account number and password


# Route to handle the update of user details
@app.route('/perform-update', methods=['POST'])
def perform_update():
    account_number = request.form['account_number']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email_id = request.form['email']
    address = request.form['address']
    phone_no = request.form['phone']
    proof_type = request.form['proof_type']
    proof_id = request.form['proof_id']
    account_type = request.form['account_type']
    occupation = request.form['occupation']
    dob = request.form['dob']
    nationality = request.form['nationality']

    con = mysql.connection.cursor()

    # Check if email already exists (excluding the current user's email)
    con.execute("SELECT * FROM user WHERE email_id = %s AND account_number != %s", (email_id, account_number))
    existing_email = con.fetchone()

    # Check if phone number already exists (excluding the current user's phone number)
    con.execute("SELECT * FROM user WHERE ph_no = %s AND account_number != %s", (phone_no, account_number))
    existing_phone = con.fetchone()

    if existing_email:
        flash("Error: This email ID is already in use.")
        con.close()
        return redirect(url_for('update_account'))

    if existing_phone:
        flash("Error: This phone number is already in use.")
        con.close()
        return redirect(url_for('update_account'))

    # Update user details in the database
    sql = """UPDATE user SET first_name = %s, last_name = %s, email_id = %s, 
              address = %s, ph_no = %s, proof_type = %s, proof_id = %s, account_type = %s, 
              occupation = %s, dob = %s, nationality = %s 
              WHERE account_number = %s"""
    con.execute(sql, (first_name, last_name, email_id, address, phone_no, proof_type, proof_id, 
                      account_type, occupation, dob, nationality, account_number))
    mysql.connection.commit()
    con.close()

    # Flash success message
    flash("Account details updated successfully!")
    return redirect(url_for('view_users'))


# Route for deleting an account
@app.route('/delete-user', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        account_number = request.form['account_number']
        password = request.form['password']
        
        con = mysql.connection.cursor()

        # Check if the account number and password exist
        con.execute("SELECT * FROM user WHERE account_number = %s AND password = %s", (account_number, password))
        account = con.fetchone()

        if account:
            # Account exists, proceed to delete
            con.execute("DELETE FROM user WHERE account_number = %s", (account_number,))
            mysql.connection.commit()
            flash("Account deleted successfully.")
        else:
            # Account not found
            flash("Account number or password is incorrect.")

        con.close()
        return redirect(url_for('view_users'))  # Redirect back to the delete account form

    return render_template('Delete_account.html')  # Render the form to delete an account


# Route to view all users (with password hidden)
@app.route('/view-users')
def view_users():
    con = mysql.connection.cursor()
    
    # Fetch all user data except for the password
    con.execute("SELECT account_number, first_name, last_name, email_id, address, ph_no, proof_type, proof_id, account_type, occupation, dob, nationality, savings_amount FROM user")
    users = con.fetchall()
    
    con.close()
    
    return render_template('view_users.html', users=users)


# <----------------------------------------------------------------------------------------------------------------------------------------------->



# User Dashboard Route
@app.route('/user_dashboard')
def user_dashboard():
    if 'user' in session:  # Check if user is logged in
        account_number = session['user']
        
        # Fetch current balance for the user
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT savings_amount FROM user WHERE account_number = %s', (account_number,))
        user_data = cursor.fetchone()
        current_balance = user_data['savings_amount'] if user_data else 0
        
        return render_template('User_dashboard.html', current_balance=current_balance)
    return redirect(url_for('user_login'))


# User Authentication Route
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        account_number = request.form['account_number']
        password = request.form['password']

        con = mysql.connection.cursor()
        # Query to check user credentials
        query = "SELECT * FROM user WHERE account_number = %s AND password = %s"
        con.execute(query, (account_number, password))
        user = con.fetchone()

        if user:
            session['user'] = account_number  # Set account number in session
            return redirect(url_for('user_dashboard'))
        else:
            return render_template('Error_page_user.html', message="Invalid User credentials")
    return render_template('User.html')


# Withdraw Cash
@app.route('/withdraw', methods=['POST'])
def withdraw_cash():
    if 'user' not in session:
        return redirect(url_for('user_login'))
    
    account_number = session['user']
    withdraw_amount = Decimal(request.form['withdraw_amount'])

    # Fetch current balance
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT first_name, last_name, savings_amount FROM user WHERE account_number = %s', (account_number,))
    user_data = cursor.fetchone()
    current_balance = user_data['savings_amount']
    username = f"{user_data['first_name']} {user_data['last_name']}"

    if withdraw_amount > current_balance:
        flash("Insufficient balance!")
    else:
        # Update balance in the user table
        new_balance = current_balance - withdraw_amount
        cursor.execute('UPDATE user SET savings_amount = %s WHERE account_number = %s', (new_balance, account_number))
        mysql.connection.commit()

        # Record transaction in the transaction table
        activity = f"withdrawed-{withdraw_amount}"
        cursor.execute('INSERT INTO transaction (username, account_number, activity) VALUES (%s, %s, %s)', 
                        (username, account_number, activity))
        mysql.connection.commit()

        flash(f"Withdrawn {withdraw_amount} successfully!")

    return redirect(url_for('user_dashboard'))


# Deposit Cash
@app.route('/deposit', methods=['POST'])
def deposit_cash():
    if 'user' not in session:
        return redirect(url_for('user_login'))

    account_number = session['user']
    deposit_amount = Decimal(request.form['deposit_amount'])

    # Fetch current balance
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT first_name, last_name, savings_amount FROM user WHERE account_number = %s', (account_number,))
    user_data = cursor.fetchone()
    current_balance = user_data['savings_amount']
    username = f"{user_data['first_name']} {user_data['last_name']}"

    # Update balance in the user table
    new_balance = current_balance + deposit_amount
    cursor.execute('UPDATE user SET savings_amount = %s WHERE account_number = %s', (new_balance, account_number))
    mysql.connection.commit()

    # Record transaction in the transaction table
    activity = f"deposited-{deposit_amount}"
    cursor.execute('INSERT INTO transaction (username, account_number, activity) VALUES (%s, %s, %s)', 
                    (username, account_number, activity))
    mysql.connection.commit()

    flash(f"Deposited {deposit_amount} successfully!")

    return redirect(url_for('user_dashboard'))


# Check Balance
@app.route('/balance', methods=['GET', 'POST'])
def check_balance():
    if 'user' not in session:
        return redirect(url_for('user_login'))

    account_number = session['user']

    # Fetch current balance from the database
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT savings_amount FROM user WHERE account_number = %s', (account_number,))
    user_data = cursor.fetchone()
    current_balance = user_data['savings_amount'] if user_data else 0

    return render_template('user_dashboard.html', current_balance=current_balance)


# View Transaction History
@app.route('/view_transaction', methods=['GET','POST'])
def view_transactions():
    if 'user' not in session:
        return redirect(url_for('user_login'))

    account_number = session['user']

    # Fetch transactions for the user
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM transaction WHERE account_number = %s', (account_number,))
    transactions = cursor.fetchall()

    return render_template('view_transactions.html', transactions=transactions)


@app.route("/user_dashboard_1")
def dashboard_1():
    return render_template('User_dashboard.html')


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    # If the request is GET, render the password change form
    if request.method == 'GET':
        return render_template('Change_password.html')
    
    # If the request is POST, process the form submission
    if request.method == 'POST':
        # Get form data
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Get the account number from the session
        account_number = session.get('user')
        
        if not account_number:
            return render_template('Change_password.html', message="No user session found.")

        # Using DictCursor to access results by column name
        con = mysql.connection.cursor(DictCursor)
        
        # Query to get the current password from the database
        query = "SELECT password FROM user WHERE account_number = %s"
        con.execute(query, (account_number,))
        result = con.fetchone()

        # Check if a result is found
        if not result:
            return render_template('Change_password.html', message="User not found.")

        current_password = result['password']  # Access by column name
        
        # Check if the old password matches the current password
        if old_password != current_password:
            return render_template('Change_password.html', message="Old password is incorrect.")
        
        # Check if the new password matches the confirmation password
        if new_password != confirm_password:
            return render_template('Change_password.html', message="New password and confirmation do not match.")
        
        # Update the password in the database
        update_query = "UPDATE user SET password = %s WHERE account_number = %s"
        con.execute(update_query, (new_password, account_number))
        mysql.connection.commit()
        
        return render_template('User.html', message="Password updated successfully.")


# <----------------------------------------------------------------------------------------------------------------------------------------------->


# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('Admin_or_User'))


if __name__ == '__main__':
    app.run(debug=True)
