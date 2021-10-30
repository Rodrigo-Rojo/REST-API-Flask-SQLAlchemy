from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
API_KEY = "TopSecretAPIKey"

##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


def cafe_to_json(cafe):
    json = {
        "id": cafe.id,
        "name": cafe.name,
        "map_url": cafe.map_url,
        "img_url": cafe.map_url,
        "location": cafe.location,
        "has_sockets": cafe.has_sockets,
        "has_wifi": cafe.has_wifi,
        "has_toilet": cafe.has_toilet,
        "can_take_calls": cafe.can_take_calls,
        "seats": cafe.seats,
        "coffee_price": cafe.coffee_price
    }
    return json


## HTTP GET - Read Record
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search")
def search_location():
    query_location = request.args.get("loc")
    try:
        cafes = Cafe.query.filter_by(location=query_location).all()
        if len(cafes) > 0:
            all_cafes = []
            for coffee in cafes:
                coffee_json = cafe_to_json(coffee)
                all_cafes.append(coffee_json)
            return jsonify(cafes=all_cafes)
        else:
            cafe = cafe_to_json(cafes)
            return jsonify(cafe=cafe)
    except AttributeError:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location"})


@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    all_cafes = []
    for coffee in cafes:
        coffee_json = cafe_to_json(coffee)
        all_cafes.append(coffee_json)
    return jsonify(all_cafes)


@app.route("/random")
def random():
    cafes = db.session.query(Cafe).all()
    cafe = cafe_to_json(choice(cafes))
    return jsonify(cafe=cafe)


## HTTP POST - Create Record
@app.route("/add", methods=["POST", "GET"])
def add_a_cafe():
    try:
        new_cafe = Cafe(
            name=request.args.get("name"),
            map_url=request.args.get("map_url"),
            img_url=request.args.get("img_url"),
            location=request.args.get("location"),
            has_sockets=bool(request.args.get("has_sockets")),
            has_wifi=bool(request.args.get("has_wifi")),
            has_toilet=bool(request.args.get("has_toilet")),
            can_take_calls=bool(request.args.get("can_take_calls")),
            seats=request.args.get("seats"),
            coffee_price=request.args.get("coffee_price")
        )
        print(new_cafe)
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe"})

    except Exception as e:
        return jsonify(response={"Error": f"Sorry, there has been an error {e}"})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["Patch", "GET"])
def update_price(cafe_id):
    try:
        cafe = Cafe.query.get(int(cafe_id))
        new_price = request.args.get("new_price")
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully Cafe price been updated."}), 200
    except Exception as e:
        return jsonify(response={"Not found": "Sorry a cafe with that id was not found in the database."}), 404


## HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE", "GET"])
def delete_closed_cafe(cafe_id):
    try:
        if request.args.get("api-key") != API_KEY:
            return jsonify(response={"Error": "Sorry, that is not allowed. Make sure you have the correct api-key."}), 403
        else:
            cafe = Cafe.query.get(int(cafe_id))
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully Cafe been deleted."}), 200
    except Exception as e:
        return jsonify(response={"Not found": "Sorry a cafe with that id was not found in the database."}), 404


if __name__ == '__main__':
    app.run(debug=True)
