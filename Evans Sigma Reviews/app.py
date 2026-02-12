import os
import sqlite3
import html
from datetime import datetime
from flask import Flask, request, redirect, session, url_for, send_from_directory, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import templates

DB = "reviews.db"
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2 MB

app = Flask(__name__, static_folder="static")

app.secret_key = os.environ.get("FLASK_SECRET") or os.urandom(24)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    MAX_CONTENT_LENGTH=MAX_UPLOAD_SIZE
)

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create database and seed movies if the DB file does not exist."""
    if os.path.exists(DB):
        return
    db = get_db()
    cur = db.cursor()
    cur.execute("""
      CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        passhash TEXT NOT NULL
      );
    """)
    cur.execute("""
      CREATE TABLE movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL
      );
    """)
    cur.execute("""
      CREATE TABLE reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        rating INTEGER NOT NULL,
        body TEXT NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY(movie_id) REFERENCES movies(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
      );
    """)
    movies = [
      ("Iron Man",),("Captain America",),("The Hulk",),("Halo Forward Unto Dawn",),
      ("Batman The Dark Knight",),("Pacific Rim",),("Transformers",),("The Fallout Show",),
      ("Power rangers SPD emergency",),("Despicable",),("Kung Fu Panda",),("Planet of the apes",),
      ("Blade Runner",),("Blade Runner 2049",),("Joker",),("Avatar",),("Breaking Bad",),
      ("Star Wars Episode IV A New Hope",),("Saving Private Ryan",),("Django",),
      ("Die Hard",),("Fast and Furious",),("21 Jump Street",),("The Avengers",),
      ("The Hunger Games",),("WALL E",),("X Men Days of Future Past",)
    ]
    cur.executemany("INSERT INTO movies (title) VALUES (?)", movies)
    db.commit()
    db.close()


init_db()


def allowed_file(filename, mimetype):
    """Return True if filename extension is allowed and mimetype looks like an image."""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXT:
        return False
    if not mimetype or not mimetype.startswith("image/"):
        return False
    return True

def nav_html():
    if session.get("user_name"):
        return f'Hello, {session["user_name"]} | <a href="/logout">Logout</a>'
    return '<a href="/login">Login</a> | <a href="/register">Register</a>'


@app.route("/")
def index():
    db = get_db()
    movies = db.execute("SELECT id, title FROM movies ORDER BY id").fetchall()
    db.close()

    summary = """
    <div class="summary">
      <h2>Welcome to New California Republic Reviews</h2>
      <p>Where you can find your friends' top hits and tips about movies in the big 26.</p>
    </div>
    """


    cards = "".join(
        templates.movie_card(m["id"], m["title"], templates.MOVIE_YEARS.get(m["id"], ""))
        for m in movies
    )

    sidebar = templates.home_sidebar(session.get("user_name"))
    content = f"{summary}<div class='layout'><div class='main'>{cards}</div>{sidebar}</div>"
    return templates.BASE_LAYOUT.format(title="NCR Reviews", nav=nav_html(), content=content)

@app.route("/movie/<int:mid>")
def movie(mid):
    db = get_db()
    m = db.execute("SELECT id, title FROM movies WHERE id = ?", (mid,)).fetchone()
    reviews = db.execute("""
      SELECT r.title, r.rating, r.body, r.date, u.name
      FROM reviews r JOIN users u ON r.user_id = u.id
      WHERE r.movie_id = ?
      ORDER BY r.date DESC
    """, (mid,)).fetchall()
    db.close()

    if not m:
        return templates.BASE_LAYOUT.format(title="Movie Not Found", nav=nav_html(), content="<p>Movie not found.</p>")

    summary_text = templates.MOVIE_SUMMARIES.get(mid, "No summary available for this title.")
    summary_html = f"<div class='movie-summary'><p>{summary_text}</p></div>"

    poster_html = ""
    posters_dir = os.path.join(app.static_folder, "posters")
    jpg_path = os.path.join(posters_dir, f"{mid}.jpg")
    png_path = os.path.join(posters_dir, f"{mid}.png")
    if os.path.exists(jpg_path):
        poster_html = f"<div class='poster'><img src='/static/posters/{mid}.jpg' alt='Poster for {m['title']}'></div>"
    elif os.path.exists(png_path):
        poster_html = f"<div class='poster'><img src='/static/posters/{mid}.png' alt='Poster for {m['title']}'></div>"

    write_link = (f'<p><a class="btn" href="/movie/{m["id"]}/review">Write review</a></p>'
                  if session.get("user_id") else '<p><a class="btn" href="/login">Log in to write a review</a></p>')

    reviews_html = "".join(templates.review_card(r["title"], r["rating"], r["body"], r["name"], r["date"]) for r in reviews) or "<p>No reviews yet.</p>"

    content = f"""
      <div class="movie-detail">
        <h2>{m['title']}</h2>
        {poster_html}
        {summary_html}
        {write_link}
        <h3>Reviews</h3>
        <div class="reviews">{reviews_html}</div>
      </div>
    """
    return templates.BASE_LAYOUT.format(title=m["title"], nav=nav_html(), content=content)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        pw = request.form.get("password", "")
        pw2 = request.form.get("confirm", "")
        if not name or not pw or pw != pw2:
            return templates.message_page("Invalid input or passwords do not match.", nav_html())
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT 1 FROM users WHERE name = ?", (name,))
        if cur.fetchone():
            db.close()
            return templates.message_page("Name already taken.", nav_html())
        h = generate_password_hash(pw)
        cur.execute("INSERT INTO users (name, passhash) VALUES (?, ?)", (name, h))
        db.commit()
        db.close()
        return redirect(url_for("login"))
    return templates.BASE_LAYOUT.format(title="Register - NCR Reviews", nav=nav_html(), content=templates.register_form())

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        pw = request.form.get("password", "")
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, name, passhash FROM users WHERE name = ?", (name,))
        row = cur.fetchone()
        db.close()
        if row and check_password_hash(row["passhash"], pw):
            session["user_id"] = row["id"]
            session["user_name"] = row["name"]
            return redirect(url_for("index"))
        return templates.message_page("Login failed.", nav_html())
    return templates.BASE_LAYOUT.format(title="Login - NCR Reviews", nav=nav_html(), content=templates.login_form())

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/movie/<int:mid>/review", methods=["GET", "POST"])
def add_review(mid):
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        rating = request.form.get("rating", "").strip()
        body = request.form.get("body", "").strip()
        if not title or not rating or not body:
            return templates.message_page("All fields required.", nav_html())
        try:
            rating = int(rating)
        except ValueError:
            return templates.message_page("Rating must be a number.", nav_html())
        if rating < 1 or rating > 5:
            return templates.message_page("Rating must be 1-5.", nav_html())
   
        safe_body = html.escape(body)
        date = datetime.now().strftime("%Y-%m-%d")
        db = get_db()
        db.execute("""INSERT INTO reviews (movie_id, user_id, title, rating, body, date)
                      VALUES (?, ?, ?, ?, ?, ?)""", (mid, session["user_id"], title, rating, safe_body, date))
        db.commit()
        db.close()
        return redirect(url_for("movie", mid=mid))
    return templates.BASE_LAYOUT.format(title="Write review - NCR Reviews", nav=nav_html(), content=templates.add_review_form(mid))

@app.route("/upload_poster", methods=["GET", "POST"])
def upload_poster():

    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        mid = request.form.get("movie_id", "").strip()
        file = request.files.get("poster")
        if not mid or not file or file.filename == "":
            return templates.message_page("Please choose a movie id and a file.", nav_html())
        if not allowed_file(file.filename, file.mimetype):
            return templates.message_page("File type not allowed.", nav_html())
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = secure_filename(f"{mid}.{ext}")
        posters_dir = os.path.join(app.static_folder, "posters")
        os.makedirs(posters_dir, exist_ok=True)
        save_path = os.path.join(posters_dir, filename)
        file.save(save_path)
        return templates.message_page("Poster uploaded.", nav_html())
    form = """
    <h2>Upload poster</h2>
    <form method="post" enctype="multipart/form-data">
      <label>Movie id<br><input name="movie_id" required></label><br>
      <label>Poster file<br><input type="file" name="poster" accept="image/*" required></label><br>
      <button type="submit" class="btn">Upload</button>
    </form>
    <p><a href="/">Back</a></p>
    """
    return templates.BASE_LAYOUT.format(title="Upload poster", nav=nav_html(), content=form)

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":

    app.run(debug=False)