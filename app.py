from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import traceback
from DRApp import predict

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'areI@03tS'
app.config['MYSQL_DB'] = 'diabeticRetinopathy'

mysql = MySQL(app)

@app.route('/predict', methods=['POST'])    
def predictHelper():
    result= predict()
    return jsonify(result)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    try:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']

            # Debug print
            print(f"DEBUG: Received login request for username: {username}")

            # Ensure database connection is active
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            try:
                # Debug print before executing query
                print("DEBUG: Executing SQL query...")

                cursor.execute('SELECT * FROM accounts WHERE userName = %s AND password = %s', (username, password))
                account = cursor.fetchone()

                # Debug print after executing query
                print(f"DEBUG: Retrieved account: {account}")

                if account:
                    session['loggedin'] = True
                    session['id'] = account['id']
                    session['username'] = account['userName']
                    msg = 'Logged in successfully!'
                    return render_template('index.html', msg=msg)
                else:
                    msg = 'Incorrect username / password!'
                    print("DEBUG: Login failed - Incorrect credentials")

            except MySQLdb.Error as db_error:
                print(f"ERROR: SQL Query failed: {str(db_error)}")
                return f"Database Error: {str(db_error)}"

    except Exception as e:
        print(f"ERROR: Internal Server Error: {str(e)}")
        return f"Internal Server Error: {str(e)}"

    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    try:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            # Debugging Statements
            print(f"DEBUG: Register - Username: {username}, Email: {email}")

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()
            print(f"DEBUG: Registration Account Check - {account}")

            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            else:
                cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
                mysql.connection.commit()
                msg = 'You have successfully registered!'
    except Exception as e:
        print(traceback.format_exc())
        return f"Internal Server Error: {str(e)}"
    
    return render_template('register.html', msg=msg)

if __name__ == '__main__':
    app.run(debug=True)

