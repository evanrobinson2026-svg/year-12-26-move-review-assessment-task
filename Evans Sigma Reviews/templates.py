MOVIE_SUMMARIES = {
    1: "A brilliant inventor is captured and builds a powered suit to escape. He returns home determined to use his technology to protect others and confront corruption (2008).",
    2: "During World War II a frail but determined young man volunteers for a secret program that transforms him into a super soldier and becomes a patriotic hero (2011).",
    3: "After a lab accident a scientist becomes a massive super strong green being. He struggles to control his rage while being hunted and learning what it means to be human (2008).",
    4: "A short live action story set in a military science fiction universe following soldiers through a tense mission that reveals loyalty and sacrifice (2012).",
    5: "A tormented vigilante adopts a masked identity to fight crime in a corrupt city, facing moral dilemmas and a rising criminal underworld (2008).",
    6: "Human pilots operate giant robots to defend Earth from enormous monsters (2013).",
    7: "Transforming alien robots arrive on Earth and clash with each other while humans are drawn into their ancient conflict (2007).",
    8: "A vault dweller must go out into a post nuclear world and experience life on the surface for the first time (2024).",
    9: "Go Go power rangers (2005).",
    10: "Minions or smth idk (2010).",
    11: "A clumsy food loving panda is chosen as the unlikely hero who must learn kung fu and protect his community from a evil tiger or smth (2008).",
    12: "In a future where apes gain higher intelligence tensions between humans and apes escalate into conflict (2011).",
    13: "A moody noir style science fiction about a detective hunting synthetic humans (1982).",
    14: "A visually striking sequel that follows a new investigator as he uncovers the consequences of advanced memory and identity technologies (2017).",
    15: "A man breaks down due to the world around him, turning into something, like a joke (2019).",
    16: "Bad humans try to invade ladn owned by tall blue aliens (2009).",
    17: "A high school chemistry teacher facing financial pressure turns to producing illegal drugs (2008).",
    18: "A young farm boy is dragged into a conflict with the terror fueled empire (1977).",
    19: "During World War II a squad undertakes a dangerous mission to rescue one paratrooper behind enemy lines (1998).",
    20: "A freed slave becomes a skilled bounty hunter and goes on a violent quest for justice and freedom (2012).",
    21: "A lone cop fights terrorists who seize control of a skyscraper in a tense action-packed fight to save hostages (1988).",
    22: "Cars go fast, and they  have race wars or smth (2001).",
    23: "Two bad cops, are selected to return to highschool undercover and bust a drug ring (2012).",
    24: "The Avengers form and fight a evil and tough foe (2012).",
    25: "In the grim future teenagers are forced to fight each other or smth 2012).",
    26: "A waste collecting robot gets picked up and becomes the true hero of earth! (2008).",
    27: "The X-Men time travel (2014)."
}

MOVIE_YEARS = {
    1: "2008", 2: "2011", 3: "2008", 4: "2012", 5: "2008",
    6: "2013", 7: "2007", 8: "2024", 9: "2005", 10: "2010",
    11: "2008", 12: "2011", 13: "1982", 14: "2017", 15: "2019",
    16: "2009", 17: "2008", 18: "1977", 19: "1998", 20: "2012",
    21: "1988", 22: "2001", 23: "2012", 24: "2012", 25: "2012",
    26: "2008", 27: "2014"
}

BASE_LAYOUT = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <header class="header" role="banner">
    <div class="brand"><a href="/"><h1>NCR Reviews</h1></a></div>
    <nav class="nav" role="navigation">{nav}</nav>
  </header>

  <main id="main-content" class="container" role="main">
    {content}
  </main>

  <footer class="footer" role="contentinfo"><small>&copy; NCR Reviews</small></footer>
</body>
</html>
"""

def movie_card(mid, title, year=""):
    poster_jpg = f"/static/posters/{mid}.jpg"
    poster_png = f"/static/posters/{mid}.png"
    year_html = f"<span class='movie-year'>{year}</span>" if year else ""
    return f"""
    <article class="card card-with-thumb" aria-labelledby="movie-{mid}-title">
      <a href="/movie/{mid}" class="card-link">
        <div class="thumb" aria-hidden="true">
          <img src="{poster_jpg}" alt="Poster for {title}" loading="lazy"
               onerror="this.onerror=null;this.src='{poster_png}';">
        </div>
        <div class="card-body">
          <div class="title-row">
            <h4 id="movie-{mid}-title" class="card-title" title="{title}">{title}</h4>
            {year_html}
          </div>
        </div>
      </a>
    </article>
    """

def home_sidebar(user_name=None):
    if user_name:
        return f"""
        <aside class="sidebar" role="complementary">
          <p>Signed in as <strong>{user_name}</strong></p>
          <p><a class="btn" href="/logout">Logout</a></p>
        </aside>
        """
    return """
    <aside class="sidebar" role="complementary">
      <div class="mini-box">
        <form action="/login" method="post" class="mini-login" aria-label="Login form">
          <input name="name" placeholder="Username" required>
          <input name="password" type="password" placeholder="Password" required>
          <button type="submit" class="btn">Login</button>
        </form>
        <p><a class="btn" href="/register">Register</a></p>
      </div>
    </aside>
    """

def register_form():
    return """
<h2>Register</h2>
<form method="post" class="form" aria-label="Register form">
  <label>Name<br><input name="name" required></label>
  <label>Password<br><input name="password" type="password" required></label>
  <label>Confirm<br><input name="confirm" type="password" required></label>
  <button type="submit" class="btn">Register</button>
</form>
"""

def login_form():
    return """
<h2>Login</h2>
<form method="post" class="form" aria-label="Login form">
  <label>Name<br><input name="name" required></label>
  <label>Password<br><input name="password" type="password" required></label>
  <button type="submit" class="btn">Login</button>
</form>
"""

def add_review_form(mid):
    return f"""
<h2>Write Review</h2>
<form method="post" class="form" aria-label="Write review form">
  <label>Title<br><input name="title" required></label>
  <label>Rating (1-5)<br><input name="rating" type="number" min="1" max="5" required></label>
  <label>Review<br><textarea name="body" rows="6" required></textarea></label>
  <button type="submit" class="btn">Submit</button>
</form>
<p><a href="/movie/{mid}">Back</a></p>
"""

def message_page(msg, nav):
    content = f"<div class='message'><p>{msg}</p><p><a class='btn' href='/'>Home</a></p></div>"
    return BASE_LAYOUT.format(title="Message - NCR Reviews", nav=nav, content=content)

def review_card(title, rating, body, author, date):
    try:
        stars = "★" * int(rating)
    except Exception:
        stars = ""
    return f"""
    <div class="review">
      <div class="review-head"><strong>{title}</strong> <span class="stars">{stars} ({rating}/5)</span></div>
      <div class="meta">by {author} on {date}</div>
      <div class="body">{body}</div>
    </div>

    """
