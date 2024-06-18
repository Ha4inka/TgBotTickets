from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS theaters (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        city_id INTEGER,
        FOREIGN KEY (city_id) REFERENCES cities (id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY,
        theater_id INTEGER,
        date TEXT,
        time TEXT,
        FOREIGN KEY (theater_id) REFERENCES theaters (id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        theater TEXT,
        date TEXT,
        session TEXT,
        phone TEXT,
        ticket_id TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        seat_number TEXT,
        status TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions (id)
    )''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM cities')
    cities = cursor.fetchall()
    conn.close()
    return render_template('index.html', cities=cities)

@app.route('/theaters', methods=['POST'])
def theaters():
    city = request.form['city']
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM theaters WHERE city_id = (SELECT id FROM cities WHERE name=?)', (city,))
    theaters = cursor.fetchall()
    conn.close()
    return render_template('theaters.html', city=city, theaters=theaters)

@app.route('/sessions', methods=['POST'])
def sessions():
    city = request.form['city']
    theater = request.form['theater']
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT date, time FROM sessions WHERE theater_id = (SELECT id FROM theaters WHERE name=?)', (theater,))
    sessions = cursor.fetchall()
    conn.close()
    return render_template('sessions.html', city=city, theater=theater, sessions=sessions)

@app.route('/seats', methods=['POST'])
def seats():
    city = request.form['city']
    theater = request.form['theater']
    date = request.form['date']
    time = request.form['time']
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT seat_number FROM seats 
    WHERE session_id = (SELECT id FROM sessions WHERE theater_id = (SELECT id FROM theaters WHERE name=?) AND date=? AND time=?) AND status="free"
    ''', (theater, date, time))
    seats = cursor.fetchall()
    conn.close()
    return render_template('seats.html', city=city, theater=theater, date=date, time=time, seats=seats)

@app.route('/book', methods=['POST'])
def book():
    city = request.form['city']
    theater = request.form['theater']
    date = request.form['date']
    time = request.form['time']
    seat = request.form['seat']
    phone = request.form['phone']
    ticket_id = f"{phone}-{theater}-{date}-{time}-{seat}"

    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO bookings (city, theater, date, session, phone, ticket_id) 
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (city, theater, date, time, phone, ticket_id))

    cursor.execute('''
    UPDATE seats SET status="occupied" WHERE session_id = (SELECT id FROM sessions WHERE theater_id = (SELECT id FROM theaters WHERE name=?) AND date=? AND time=?) AND seat_number=?
    ''', (theater, date, time, seat))

    conn.commit()
    conn.close()

    return render_template('confirmation.html', ticket_id=ticket_id)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
