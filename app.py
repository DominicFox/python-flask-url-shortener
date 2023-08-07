import string
import random
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import functions
import os

# Initialise Flask app
app = Flask(__name__)

# Create config options for our SQLite database
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(base_dir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def shorten_url(length=6):
    # Generate a random string of length 6 using numbers and uppercase/lowercase letters
    char_set = string.ascii_letters + string.digits
    short_url_string = "".join(random.choice(char_set) for _ in range(length))
    return short_url_string


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user input url to shorten
        long_url_input = request.form['longurl']

        # Check if this url is already in the database
        duplicate_long_url_list = URLMapping.query.filter_by(
            long_url=long_url_input).all()
        if not duplicate_long_url_list:
            short_url_output = shorten_url()

            # Ensure our random short_url_output is unique
            while URLMapping.query.get(short_url_output):
                short_url_output = shorten_url()

            # Construct new short url and add it to database
            new_url = URLMapping(short_url=short_url_output,
                                 long_url=long_url_input)
            db.session.add(new_url)
            db.session.commit()
        else:
            # If we've already mapped this long url then just retrieve short url from database record
            short_url_output = duplicate_long_url_list[0].short_url

        full_url_output = request.url + short_url_output
        return render_template("index.html", short_url=full_url_output, maps=URLMapping.query.all())

    return render_template("index.html", maps=URLMapping.query.all())


@app.route("/<short_url_input>")
def redirect_url(short_url_input):
    # Redirect a short url to the correct long url, or return error 404 if not in database.
    long_url_output = URLMapping.query.get_or_404(short_url_input).long_url
    return redirect(long_url_output)


class URLMapping(db.Model):
    short_url = db.Column(db.String(30), primary_key=True)
    long_url = db.Column(db.String(2000), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=functions.now())

    def __repr__(self):
        return f'<ShortURL: {self.short_url}>'
