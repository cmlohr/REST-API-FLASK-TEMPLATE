from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Bar Database Configuration
class Bars(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    beer_price = db.Column(db.String(250), nullable=True)

    # send to dict to store all the data
    def to_dict(self):
        # method 1
        # dictionary = {}
        # for column in self.__table__.columns:
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary
        # method 2 comprehension
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# creates the database
# db.create_all()


# begin routes
@app.route("/")
def home():
    return render_template("index.html")


# selects a random item in database
@app.route("/random")
def get_random_bar():
    bar = db.session.query(Bars).all()
    random_bar = random.choice(bar)
    return jsonify(bar=random_bar.to_dict())


# selects all items in database
@app.route("/all")
def get_all():
    bars = db.session.query(Bars).all()
    return jsonify(bars=[bars.to_dict() for bars in bars])


# allows search by location
@app.route("/search")
def search():
    query_location = request.args.get("loc")
    bars = db.session.query(Bars).filter_by(location=query_location).first()
    if bars:
        return jsonify(bars=bars.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, no record found."})


# adds item to database
@app.route("/add", methods=["POST"])
def add_bars():
    new_bars = Bars(
        name=request.form.get("name"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        seats=request.form.get("seats"),
        beer_price=request.form.get("beer_price"),
    )
    db.session.add(new_bars)
    db.session.commit()
    return jsonify(response={"success": "Successfully added bar."})


# Patches price within the database
@app.route("/update-price/<int:bars_id>", methods=["PATCH"])
def patch_update_price(bars_id):
    new_price = request.args.get("new_price")
    bars = db.session.query(Bars).get(bars_id)
    if bars:
        bars.beer_price = new_price
        db.session.commit()
        return jsonify(response={"Success": "Successfully updated."})
    else:
        return jsonify(error={"Not Found": "ID not found in database."})


# deletes item in database
@app.route("/report-closed/<int:bars_id>", methods=["DELETE"])
def delete_bar(bars_id):
    api_key = request.args.get("api-key")
    if api_key == "MySecret":
        bars = db.session.query(Bars).get(bars_id)
        if bars:
            db.session.delete(bars)
            db.session.commit()
            return jsonify(response={"success": "Item deleted"}), 200
        else:
            return jsonify(error={"not found": "No item with that ID was found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "You are not authorized."}), 403


# flexible format method 3 allows for more flexable random
# @app.route("/random")
# def get_random_bar():
#     bars = db.session.query(Bar).all()
#     random_bar = random.choice(bars)
#     return jsonify(bar={
#         "id": random_bar.id,
#         "name": random_bar.name,
#         "location": random_bar.location,
#         "seats": random_bar.seats,
#         "has_toilet": random_bar.has_toilet,
#         "has_wifi": random_bar.has_wifi,
#         "has_sockets": random_bar.has_sockets,
#         "beer_price": random_bar.beer_price,
#     })


if __name__ == '__main__':
    app.run(debug=True)
