from flask import Flask, render_template
import json

app = Flask(__name__)

def load():
    with open("data.json") as f:
        return json.load(f)

@app.route("/")
def home():
    data = load()
    teams = data["teams"]

    sorted_teams = sorted(
        teams.items(),
        key=lambda x: (x[1]["P"], x[1]["W"]),
        reverse=True
    )

    return render_template("index.html", teams=sorted_teams)

@app.route("/admin")
def admin():
    return "<h1>Admin Panel Coming Soon 😈</h1>"

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)