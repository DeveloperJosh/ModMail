from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
# import db from utils\database.py
from utils.database import db
from utils.config import guild, username, password
    
app = Flask(__name__, template_folder='html', static_folder='static')

@app.route("/", methods=['GET', 'POST'])
def index():
     if request.method == 'POST':
        # check login details from config.py
        if request.form['username'] == username and request.form['password'] == password:
            cookie = make_response(redirect(url_for('dashboard')))
            cookie.set_cookie('logged_in', 'true')
            return cookie
        else:
            return render_template('bad_pass.html')
     else:
        return render_template('index.html')

@app.route("/update/category" , methods=['POST'])
def update_category():
     category= request.form
     id = category['id']
     id = int(id)
     print(id)
     if db.servers.find_one({'_id': guild}):
        db.servers.update_one({'_id': guild}, {'$set': {'category': id}})
        return redirect(url_for('index'))
     else:
        return jsonify({"Error": "You need to run !setup first"})

@app.route("/dashboard")
def dashboard():
     if request.cookies.get('logged_in') == 'true':
        return render_template('dashboard.html')
     else:
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)