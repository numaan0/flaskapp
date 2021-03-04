from flask import Flask, render_template, request, session, redirect, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
conn = mysql.connector.connect(host="localhost", user="root", password="", database="client")
cursor = conn.cursor()

x=0

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('signup.html')


@app.route('/home')
def home():
    if 'sno' in session:
        return render_template('home.html')
    else:
        return redirect('/')


@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(email, password))
    users = cursor.fetchall()
    if len(users) > 0:
        session['sno'] = users[0][0]
        return redirect('/home')
    else:
        return redirect('/')


@app.route('/add_user', methods=['POST'])
def add_user():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    age = request.form.get('age')
    gender = request.form.get('gender')
    email = request.form.get('uemail')
    password = request.form.get('upassword')
    cnic = request.form.get('cnic')
    cursor.execute("""INSERT INTO `users` (`sno`,`firstname`,`lastname`,`age`,`gender`,`email`,`password`,`cnic`) 
    VALUES (NULL,'{}','{}','{}','{}','{}','{}','{}')""".format(fname, lname, age, gender, email, password, cnic))
    conn.commit()

    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}'""".format(email))
    myuser = cursor.fetchall()
    session['sno'] = myuser[0][0]
    return redirect('/home')


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if 'sno' in session:
        if request.method=="GET":
            user = session['sno']
            cursor = conn.cursor()
            # cursor.execute("SELECT firstname,lastname,age,cnic,gender,email,password FROM users WHERE sno= '" + user +"'")
            cursor.execute("select * from users where sno like '{}'".format(user))
            r=cursor.fetchone()
            conn.commit()
            return render_template('profile.html',r=r)
    else:
        return redirect('/')

"""            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            age = request.form.get('age')
            cnic = request.form.get('cnic')
            gender = request.form.get('gender')
            email = request.form.get('email')
            password = request.form.get('password')"""


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    if 'sno' in session:
        if request.method=='POST':
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            age = request.form.get('age')
            cnic = request.form.get('cnic')
            gender = request.form.get('gender')
            password = request.form.get('password')
            user = session['sno']
            cursor = conn.cursor()
            cursor.execute("""
                          UPDATE users
                          SET firstname=%s, lastname=%s, age=%s,cnic=%s,gender=%s,password=%s
                          WHERE sno=%s
                       """, (firstname, lastname, age, cnic,gender,password,user))
            flash("Data Updated Successfully")
            conn.commit()
        return render_template('edit.html')
    else:
        return redirect('/')







@app.route('/logout')
def logout():
    session.pop('sno')
    return redirect('/')


@app.route("/dashboard", methods=['GET', 'POST'])
def admin():
    if ('user' in session and session['user'] == 'admin'):
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM `users`""")
        data = cursor.fetchall()
        return render_template('dashboard.html', students=data)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == 'admin' and userpass == 'admin'):
            session['user'] = username
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM `users`""")
            data = cursor.fetchall()

            return render_template('dashboard.html', students=data)

    return render_template('admin.html')


@app.route('/logout_admin')
def logout_admin():
    session.pop('user')
    return redirect('/dashboard')


@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    if ('user' in session and session['user'] == 'admin'):

        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE sno = '{}'".format(id_data))
        conn.commit()
        flash("Done!")
    return redirect('/dashboard')


@app.route('/result', methods=['POST', 'GET'])
def result():
    cursor = conn.cursor()
    if request.method == 'POST':
        result = request.form
        name = result['Name']
        cursor.execute(
            "SELECT sno,firstname,lastname,age,cnic,gender,email,password FROM users WHERE firstname='" + name + "'")
        r = cursor.fetchone()
        conn.commit()
        return render_template('result.html', r=r)


app.run(debug=True)
