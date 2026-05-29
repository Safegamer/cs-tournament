from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "secret123"  # change later

DATA_FILE = "data.json"

# 🔐 LOGIN DETAILS
USERNAME = "admin"
PASSWORD = "1234"


def load():
    try:
        with open(DATA_FILE) as f:
            data = json.load(f)

            # Ensure RD exists for old teams
            for team in data["teams"]:
                if "RD" not in data["teams"][team]:
                    data["teams"][team]["RD"] = 0

            return data
    except:
        return {"teams": {}}


def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/")
def home():
    data = load()
    teams = data["teams"]

    sorted_teams = sorted(
        teams.items(),
        key=lambda x: (x[1]["P"], x[1].get("RD", 0)),  # RD as tiebreaker
        reverse=True
    )

    return render_template("index.html", teams=sorted_teams)


# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        if user == USERNAME and pwd == PASSWORD:
            session["user"] = user
            return redirect("/admin")

        return "Invalid credentials ❌"

    return render_template("login.html")


# 🔐 LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# 🔐 ADMIN PANEL
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "user" not in session:
        return redirect("/login")

    data = load()

    if request.method == "POST":
        team = request.form.get("team")

        if team:
            data["teams"][team] = {
                "M": 0,
                "W": 0,
                "L": 0,
                "D": 0,
                "RD": 0,  # ✅ NEW FIELD
                "P": 0
            }
            save(data)

        return redirect("/admin")

    return render_template("admin.html", teams=data["teams"])


# 🔐 EDIT TEAM
@app.route("/edit/<team>", methods=["GET", "POST"])
def edit(team):
    if "user" not in session:
        return redirect("/login")

    data = load()

    if team not in data["teams"]:
        return "Team not found"

    if request.method == "POST":
        M = int(request.form.get("M") or 0)
        W = int(request.form.get("W") or 0)
        D = int(request.form.get("D") or 0)
        L = int(request.form.get("L") or 0)
        RD = int(request.form.get("RD") or 0)  # ✅ NEW

        P = W * 3 + D  # Points logic unchanged

        data["teams"][team] = {
            "M": M,
            "W": W,
            "L": L,
            "D": D,
            "RD": RD,
            "P": P
        }

        save(data)
        return redirect("/admin")

    return render_template("edit.html", team=team, data=data["teams"][team])


# 🔐 DELETE
@app.route("/delete/<team>")
def delete(team):
    if "user" not in session:
        return redirect("/login")

    data = load()
    data["teams"].pop(team, None)
    save(data)
    return redirect("/admin")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
