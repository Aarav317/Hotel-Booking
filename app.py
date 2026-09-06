from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "dineahead-secret-key"

# ==============================
# DATABASE CONNECTION
# ==============================

def get_db():
    connection = sqlite3.connect("dineahead.db")
    connection.row_factory = sqlite3.Row
    return connection


# ==============================
# CREATE DATABASE
# ==============================

def create_database():

    connection = get_db()

    # Create bookings table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            hotel TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            guests INTEGER NOT NULL,
            status TEXT DEFAULT 'Confirmed'
        )
    """)

    # Add status column to old database
    try:

        connection.execute(
            "ALTER TABLE bookings ADD COLUMN status TEXT DEFAULT 'Confirmed'"
        )

        connection.commit()

    except sqlite3.OperationalError:

        # Status column already exists
        pass


    # Create users table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)


    # Add user_id column to old bookings table
    try:

        connection.execute(
            "ALTER TABLE bookings ADD COLUMN user_id INTEGER"
        )

        connection.commit()

    except sqlite3.OperationalError:

        # user_id column already exists
        pass


    connection.commit()
    connection.close()

    
# ==============================
# HOME PAGE
# ==============================

@app.route("/")
def home():
    return render_template("index.html")


# ==============================
# MENU PAGE
# ==============================

@app.route("/menu")
def menu():
    return render_template("menu.html")

# ==============================
# REGISTER PAGE
# ==============================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Convert password into secure hash
        password_hash = generate_password_hash(password)

        connection = get_db()

        try:

            connection.execute("""
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
            """, (name, email, password_hash))

            connection.commit()
            connection.close()

            return """
            <html>
            <head>
                <title>Registration Successful</title>
            </head>

            <body style="text-align:center; padding:60px; font-family:Arial;">

                <h1>Account Created! 🎉</h1>

                <p>Your DineAhead account has been created successfully.</p>

                <a href="/login">
                    Go to Login
                </a>

            </body>
            </html>
            """

        except sqlite3.IntegrityError:

            connection.close()

            return """
            <html>
            <head>
                <title>Email Already Exists</title>
            </head>

            <body style="text-align:center; padding:60px; font-family:Arial;">

                <h1>Email Already Registered ❌</h1>

                <p>
                    An account with this email already exists.
                </p>

                <a href="/register">
                    Try Another Email
                </a>

            </body>
            </html>
            """

    return render_template("register.html")

# ==============================
# LOGIN PAGE
# ==============================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db()

        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()

        # Check user and password
        if user and check_password_hash(user["password"], password):

            # Save user information in session
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]

            return redirect("/")

        else:

            return """
            <html>

            <body style="
                text-align:center;
                padding:60px;
                font-family:Arial;
                background:#f5f1eb;
            ">

                <h1>Login Failed ❌</h1>

                <p>
                    Email or password is incorrect.
                </p>

                <a href="/login">
                    Try Again
                </a>

            </body>

            </html>
            """

    return render_template("login.html")


# ==============================
# BOOKING PAGE
# ==============================

@app.route("/booking", methods=["GET", "POST"])
def booking():

    # User must be logged in
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        name = request.form["name"]
        hotel = request.form["hotel"]
        date = request.form["date"]
        time = request.form["time"]
        guests = request.form["guests"]

        connection = get_db()

        # Save booking with logged-in user's ID
        cursor = connection.execute("""
            INSERT INTO bookings
            (name, hotel, date, time, guests, status, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            hotel,
            date,
            time,
            guests,
            "Confirmed",
            session["user_id"]
        ))

        connection.commit()

        booking_id = cursor.lastrowid

        connection.close()

        # Confirmation page
        return f"""
        <!DOCTYPE html>

        <html>
        <head>

            <title>Booking Confirmed - DineAhead</title>

            <style>

                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f5f1eb;
                    text-align: center;
                    padding: 60px;
                }}

                .confirmation {{
                    background-color: white;
                    max-width: 600px;
                    margin: auto;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                }}

                h1 {{
                    color: #e8a83e;
                }}

                p {{
                    font-size: 18px;
                    margin: 12px;
                }}

                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 25px;
                    background-color: #e8a83e;
                    color: black;
                    text-decoration: none;
                    border-radius: 5px;
                }}

            </style>

        </head>

        <body>

            <div class="confirmation">

                <h1>Booking Confirmed! 🎉</h1>

                <p>
                    <b>Booking ID:</b> #{booking_id}
                </p>

                <p>
                    Hello <b>{name}</b>!
                </p>

                <p>
                    Your table has been successfully booked.
                </p>

                <hr>

                <p>
                    <b>Hotel:</b> {hotel}
                </p>

                <p>
                    <b>Date:</b> {date}
                </p>

                <p>
                    <b>Time:</b> {time}
                </p>

                <p>
                    <b>Guests:</b> {guests}
                </p>

                <p>
                    <b>Status:</b> Confirmed
                </p>

                <a href="/my-bookings">
                    My Bookings
                </a>

                <br>

                <a href="/">
                    Back to Home
                </a>

            </div>

        </body>
        </html>
        """

    return render_template("booking.html")

# ==============================
# MY BOOKINGS
# ==============================

@app.route("/my-bookings")
def my_bookings():

    # User must be logged in
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db()

    bookings = connection.execute("""
        SELECT *
        FROM bookings
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    connection.close()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )
# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():

    # Clear login session
    session.clear()

    # Go back to home page
    return redirect("/")

# ==============================
# USER CANCEL PAGE
# ==============================

@app.route("/cancel")
def cancel_page():

    return render_template("cancel.html")


# ==============================
# USER CANCEL BOOKING
# ==============================

@app.route("/cancel-booking", methods=["POST"])
def cancel_booking_form():

    booking_id = request.form["booking_id"]

    connection = get_db()

    booking = connection.execute(
        "SELECT * FROM bookings WHERE id = ?",
        (booking_id,)
    ).fetchone()

    # Booking doesn't exist
    if booking is None:

        connection.close()

        return """
        <html>
        <body style="text-align:center; padding:60px;">

            <h2>Booking Not Found ❌</h2>

            <p>
                Please check your Booking ID.
            </p>

            <a href="/cancel">
                Try Again
            </a>

        </body>
        </html>
        """


    # Already cancelled
    if booking["status"] == "Cancelled":

        connection.close()

        return """
        <html>
        <body style="text-align:center; padding:60px;">

            <h2>Booking Already Cancelled ❌</h2>

            <p>
                This booking has already been cancelled.
            </p>

            <a href="/cancel">
                Back
            </a>

        </body>
        </html>
        """


    # Cancel booking
    connection.execute(
        """
        UPDATE bookings
        SET status = 'Cancelled'
        WHERE id = ?
        """,
        (booking_id,)
    )

    connection.commit()
    connection.close()


    # Cancellation confirmation
    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Booking Cancelled - DineAhead</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f1eb;
                text-align: center;
                padding: 60px;
            }}

            .box {{
                background-color: white;
                max-width: 600px;
                margin: auto;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }}

            h1 {{
                color: #d9534f;
            }}

            p {{
                font-size: 18px;
            }}

            a {{
                display: inline-block;
                margin-top: 20px;
                padding: 12px 25px;
                background-color: #e8a83e;
                color: black;
                text-decoration: none;
                border-radius: 5px;
            }}

        </style>

    </head>

    <body>

        <div class="box">

            <h1>Booking Cancelled ❌</h1>

            <p>
                Your booking has been successfully cancelled.
            </p>

            <p>
                <b>Booking ID:</b> #{booking_id}
            </p>

            <a href="/">
                Back to Home
            </a>

        </div>

    </body>

    </html>
    """


# ==============================
# ADMIN DELETE BOOKING
# ==============================

@app.route("/delete/<int:id>")
def delete_booking(id):

    connection = get_db()

    connection.execute(
        "DELETE FROM bookings WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect("/admin")


# ==============================
# ADMIN DASHBOARD
# ==============================


@app.route("/admin")
def admin():

    connection = get_db()

    # Get all bookings
    bookings = connection.execute(
        "SELECT * FROM bookings ORDER BY id DESC"
    ).fetchall()

    # Total bookings
    total_bookings = connection.execute(
        "SELECT COUNT(*) FROM bookings"
    ).fetchone()[0]

    # Total guests
    total_guests = connection.execute(
        "SELECT SUM(guests) FROM bookings WHERE status = 'Confirmed'"
    ).fetchone()[0]

    # If there are no confirmed bookings
    if total_guests is None:
        total_guests = 0

    # Today's bookings
    today = connection.execute(
        """
        SELECT COUNT(*) FROM bookings
        WHERE date = date('now', 'localtime')
        AND status = 'Confirmed'
        """
    ).fetchone()[0]

    connection.close()

    return render_template(
        "admin.html",
        bookings=bookings,
        total_bookings=total_bookings,
        total_guests=total_guests,
        today_bookings=today
    )


# ==============================
# START FLASK
# ==============================

if __name__ == "__main__":

    create_database()

    app.run(
        debug=False,
        use_reloader=False
    )