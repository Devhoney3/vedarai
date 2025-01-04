from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from models import init_db

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the database
init_db()

@app.route('/')
def home():
    conn = sqlite3.connect('betting_prediction.db')
    c = conn.cursor()
    c.execute("SELECT * FROM predictions")
    predictions = c.fetchall()
    c.execute("SELECT * FROM blogs")
    blogs = c.fetchall()
    conn.close()

    total_wins = sum(1 for prediction in predictions if prediction[5] == 'win')
    total_losses = sum(1 for prediction in predictions if prediction[5] == 'loss')

    return render_template('home.html', total_wins=total_wins, total_losses=total_losses, blogs=blogs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['role'] = user[3]
            if user[3] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user[3] == 'user':
                return redirect(url_for('user_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'user'  # Default role for new users
        address = request.form['address']

        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role, address) VALUES (?, ?, ?, ?)", (username, password, role, address))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session and session['role'] == 'admin':
        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("SELECT * FROM predictions ORDER BY id DESC")
        predictions = c.fetchall()
        c.execute("SELECT * FROM blogs")
        blogs = c.fetchall()
        conn.close()

        total_wins = sum(1 for prediction in predictions if prediction[5] == 'win')
        total_losses = sum(1 for prediction in predictions if prediction[5] == 'loss')

        return render_template('admin_dashboard.html', predictions=predictions, total_wins=total_wins, total_losses=total_losses, blogs=blogs)
    else:
        return redirect(url_for('login'))

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' in session and session['role'] == 'user':
        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("SELECT * FROM predictions ORDER BY id DESC")
        predictions = c.fetchall()
        conn.close()

        total_wins = sum(1 for prediction in predictions if prediction[5] == 'win')
        total_losses = sum(1 for prediction in predictions if prediction[5] == 'loss')

        return render_template('user_dashboard.html', predictions=predictions, total_wins=total_wins, total_losses=total_losses)
    else:
        return redirect(url_for('login'))

@app.route('/admin/create_prediction', methods=['GET', 'POST'])
def create_prediction():
    if 'user_id' in session and session['role'] == 'admin':
        if request.method == 'POST':
            match_name = request.form['match_name']
            match_time = request.form['match_time']
            prediction_text = request.form['prediction']
            odds = request.form['odds']
            result = request.form.get('result', 'pending')  # Default to 'pending' if not provided
            premium = request.form.get('premium', 0)  # Default to 0 if not provided

            conn = sqlite3.connect('betting_prediction.db')
            c = conn.cursor()
            c.execute("INSERT INTO predictions (match_name, match_time, prediction, odds, result, premium) VALUES (?, ?, ?, ?, ?, ?)",
                      (match_name, match_time, prediction_text, odds, result, premium))
            conn.commit()
            conn.close()

            return redirect(url_for('admin_dashboard'))

        return render_template('create_prediction.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin/update_prediction/<int:prediction_id>', methods=['GET', 'POST'])
def update_prediction(prediction_id):
    if 'user_id' in session and session['role'] == 'admin':
        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("SELECT * FROM predictions WHERE id=?", (prediction_id,))
        prediction = c.fetchone()
        conn.close()

        if request.method == 'POST':
            match_name = request.form['match_name']
            match_time = request.form['match_time']
            prediction_text = request.form['prediction']
            odds = request.form['odds']
            result = request.form['result']
            premium = request.form.get('premium', 0)  # Default to 0 if not provided

            conn = sqlite3.connect('betting_prediction.db')
            c = conn.cursor()
            c.execute("UPDATE predictions SET match_name=?, match_time=?, prediction=?, odds=?, result=?, premium=? WHERE id=?",
                      (match_name, match_time, prediction_text, odds, result, premium, prediction_id))
            conn.commit()
            conn.close()

            return redirect(url_for('admin_dashboard'))

        return render_template('update_prediction.html', prediction=prediction)
    else:
        return redirect(url_for('login'))

@app.route('/admin/delete_prediction/<int:prediction_id>')
def delete_prediction(prediction_id):
    if 'user_id' in session and session['role'] == 'admin':
        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("DELETE FROM predictions WHERE id=?", (prediction_id,))
        conn.commit()
        conn.close()

        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/user/add_feedback/<int:prediction_id>', methods=['GET', 'POST'])
def add_feedback(prediction_id):
    if 'user_id' in session and session['role'] == 'user':
        if request.method == 'POST':
            feedback = request.form['feedback']

            conn = sqlite3.connect('betting_prediction.db')
            c = conn.cursor()
            c.execute("UPDATE predictions SET feedback=? WHERE id=?", (feedback, prediction_id))
            conn.commit()
            conn.close()

            return redirect(url_for('user_dashboard'))

        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("SELECT * FROM predictions WHERE id=?", (prediction_id,))
        prediction = c.fetchone()
        conn.close()

        return render_template('add_feedback.html', prediction=prediction)
    else:
        return redirect(url_for('login'))

@app.route('/admin/edit_stats', methods=['GET', 'POST'])
def edit_stats():
    if 'user_id' in session and session['role'] == 'admin':
        if request.method == 'POST':
            total_wins = request.form['total_wins']
            total_losses = request.form['total_losses']

            conn = sqlite3.connect('betting_prediction.db')
            c = conn.cursor()
            c.execute("UPDATE stats SET total_wins=?, total_losses=? WHERE id=1", (total_wins, total_losses))
            conn.commit()
            conn.close()

            return redirect(url_for('admin_dashboard'))

        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("SELECT * FROM stats WHERE id=1")
        stats = c.fetchone()
        conn.close()

        return render_template('edit_stats.html', stats=stats)
    else:
        return redirect(url_for('login'))

@app.route('/neural_bets')
def neural_bets():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("SELECT neural_access FROM users WHERE id=?", (user_id,))
        neural_access = c.fetchone()
        conn.close()

        if neural_access and neural_access[0] == 1:
            return render_template('neural_bets.html')
        else:
            return render_template('payment.html')
    else:
        return redirect(url_for('login'))

@app.route('/premium_tips')
def premium_tips():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("SELECT premium_access FROM users WHERE id=?", (user_id,))
        premium_access = c.fetchone()
        conn.close()

        if premium_access and premium_access[0] == 1:
            conn = sqlite3.connect('betting_prediction.db')
            c = conn.cursor()
            c.execute("SELECT * FROM predictions WHERE premium=1 ORDER BY id DESC")
            predictions = c.fetchall()
            conn.close()

            return render_template('premium_tips.html', predictions=predictions)
        else:
            return render_template('premium_payment.html')
    else:
        return redirect(url_for('login'))

@app.route('/process_payment', methods=['GET', 'POST'])
def process_payment():
    if request.method == 'POST':
        utr_number = request.form['utr_number']
        user_id = session['user_id']

        # Here you can add your logic to verify the UTR number and update the user's access
        # For now, we'll just simulate the payment process

        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("UPDATE users SET neural_access=1, payment_pending=1 WHERE id=?", (user_id,))
        conn.commit()
        conn.close()

        return redirect(url_for('neural_bets'))

    return render_template('payment.html')

@app.route('/process_premium_payment', methods=['GET', 'POST'])
def process_premium_payment():
    if request.method == 'POST':
        utr_number = request.form['utr_number']
        user_id = session['user_id']

        # Here you can add your logic to verify the UTR number and update the user's access
        # For now, we'll just simulate the payment process

        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("UPDATE users SET premium_access=1, payment_pending=1 WHERE id=?", (user_id,))
        conn.commit()
        conn.close()

        return redirect(url_for('premium_tips'))

    return render_template('premium_payment.html')

@app.route('/admin/approve_payment/<int:user_id>', methods=['GET', 'POST'])
def approve_payment(user_id):
    if 'user_id' in session and session['role'] == 'admin':
        if request.method == 'POST':
            conn = sqlite3.connect('betting_prediction.db')
            c = conn.cursor()
            c.execute("UPDATE users SET payment_pending=0 WHERE id=?", (user_id,))
            conn.commit()
            conn.close()

            return redirect(url_for('admin_dashboard'))

        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = c.fetchone()
        conn.close()

        return render_template('approve_payment.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/admin/free_predictions')
def admin_free_predictions():
    if 'user_id' in session and session['role'] == 'admin':
        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("SELECT * FROM predictions WHERE premium=0 ORDER BY id DESC")
        predictions = c.fetchall()
        conn.close()

        return render_template('admin_free_predictions.html', predictions=predictions)
    else:
        return redirect(url_for('login'))

@app.route('/admin/neural_ai_predictions')
def admin_neural_ai_predictions():
    if 'user_id' in session and session['role'] == 'admin':
        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("SELECT * FROM predictions WHERE premium=1 ORDER BY id DESC")
        predictions = c.fetchall()
        conn.close()

        return render_template('admin_neural_ai_predictions.html', predictions=predictions)
    else:
        return redirect(url_for('login'))

@app.route('/admin/create_blog', methods=['GET', 'POST'])
def create_blog():
    if 'user_id' in session and session['role'] == 'admin':
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            image_url = request.form['image_url']

            conn = sqlite3.connect('betting_prediction.db')
            c = conn.cursor()
            c.execute("INSERT INTO blogs (title, content, image_url) VALUES (?, ?, ?)",
                      (title, content, image_url))
            conn.commit()
            conn.close()

            return redirect(url_for('admin_dashboard'))

        return render_template('create_blog.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin/update_blog/<int:blog_id>', methods=['GET', 'POST'])
def update_blog(blog_id):
    if 'user_id' in session and session['role'] == 'admin':
        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("SELECT * FROM blogs WHERE id=?", (blog_id,))
        blog = c.fetchone()
        conn.close()

        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            image_url = request.form['image_url']

            conn = sqlite3.connect('betting_prediction.db')
            c = conn.cursor()
            c.execute("UPDATE blogs SET title=?, content=?, image_url=? WHERE id=?",
                      (title, content, image_url, blog_id))
            conn.commit()
            conn.close()

            return redirect(url_for('admin_dashboard'))

        return render_template('update_blog.html', blog=blog)
    else:
        return redirect(url_for('login'))

@app.route('/admin/delete_blog/<int:blog_id>')
def delete_blog(blog_id):
    if 'user_id' in session and session['role'] == 'admin':
        conn = sqlite3.connect('betting_prediction.db')
        c = conn.cursor()
        c.execute("DELETE FROM blogs WHERE id=?", (blog_id,))
        conn.commit()
        conn.close()

        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
