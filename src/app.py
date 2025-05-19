"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Starship

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


def get_current_user():
    user = User.query.get(1)
    if not user:
        raise APIException("User not found", status_code=404)
    return user


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)

# PEOPLE 
@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    return jsonify([p.serialize() for p in people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"message": "Person not found"}), 404
    return jsonify(person.serialize()), 200

# PLANETS 
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"message": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

# STARSHIPS
@app.route('/starships', methods=['GET'])
def get_all_starships():
    starships = Starship.query.all()
    return jsonify([s.serialize() for s in starships]), 200

@app.route('/starships/<int:starship_id>', methods=['GET'])
def get_one_starship(starship_id):
    starship = Starship.query.get(starship_id)
    if starship is None:
        return jsonify({"message": "Starship not found"}), 404
    return jsonify(starship.serialize()), 200

# USUARIOS
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user = get_current_user()
    return jsonify({
        "favorite_planets": [p.serialize() for p in user.planet_favorite],
        "favorite_people": [p.serialize() for p in user.people_favorite],
        "favorite_starships": [s.serialize() for s in user.starship_favorite]
    }), 200

# FAVORITOS

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_fav_planet(planet_id):
    user = get_current_user()
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"message": "Planet not found"}), 404
    if planet in user.planet_favorite:
        return jsonify({"message": "Planet already in favorites"}), 400

    user.planet_favorite.append(planet)
    db.session.commit()
    return jsonify({"message": "Planet added to favorites", "planet": planet.serialize()}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_fav_planet(planet_id):
    user = get_current_user()
    planet = Planet.query.get(planet_id)
    if not planet or planet not in user.planet_favorite:
        return jsonify({"message": "Planet not in favorites"}), 404

    user.planet_favorite.remove(planet)
    db.session.commit()
    return jsonify({"message": "Planet removed from favorites", "planet": planet.serialize()}), 200


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user = get_current_user()
    people = People.query.get(people_id)
    if not people:
        return jsonify({"message": "Character not found"}), 404
    if people in user.people_favorite:
        return jsonify({"message": "Character already in favorites"}), 400

    user.people_favorite.append(people)
    db.session.commit()
    return jsonify({"message": f"{people.name} added to favorites", "character": people.serialize()}), 201

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user = get_current_user()
    people = People.query.get(people_id)
    if not people:
        return jsonify({"message": "Character not found"}), 404
    if people not in user.people_favorite:
        return jsonify({"message": "Character not in favorites"}), 400

    user.people_favorite.remove(people)
    db.session.commit()
    return jsonify({"message": f"{people.name} removed from favorites", "character": people.serialize()}), 200


@app.route('/favorite/starship/<int:starship_id>', methods=['POST'])
def add_fav_starship(starship_id):
    user = get_current_user()
    starship = Starship.query.get(starship_id)
    if not starship:
        return jsonify({"message": "Starship not found"}), 404
    if starship in user.starship_favorite:
        return jsonify({"message": "Starship already in favorites"}), 400

    user.starship_favorite.append(starship)
    db.session.commit()
    return jsonify({"message": "Starship added to favorites", "starship": starship.serialize()}), 201

@app.route('/favorite/starship/<int:starship_id>', methods=['DELETE'])
def remove_fav_starship(starship_id):
    user = get_current_user()
    starship = Starship.query.get(starship_id)
    if not starship or starship not in user.starship_favorite:
        return jsonify({"message": "Starship not in favorites"}), 404

    user.starship_favorite.remove(starship)
    db.session.commit()
    return jsonify({"message": "Starship removed from favorites", "starship": starship.serialize()}), 200


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
