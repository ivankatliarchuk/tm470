from tm470webapp import app

# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click here to get to Admin!</a>'
