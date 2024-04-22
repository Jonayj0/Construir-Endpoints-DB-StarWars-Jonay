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
from models import db, User, Characters, Planets, Vehicles, FavoritesCharacters, FavoritesPlanets, FavoritesVehicles
#from models import Person

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

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#ENDPOINT lista de Todos los Usuarios-----------------------------------------------------------------------------------
@app.route('/users', methods=['GET'])
def get_all_users():

    query_results = User.query.all()
    results = list(map(lambda item: item.serialize(), query_results))
    # print(results)
    if results == []:
        return jsonify({"msg":"Empty"}), 404

    response_body = {
        "msg": "Ok",
        "result": results
    }

    return jsonify(response_body), 200


#ENDPOINT lista de Todos los Favoritos=['GET'])-----------------------------------------------------------------
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    favorite_character = FavoritesCharacters.query.all()
    character_favorite = list(map(lambda item: item.serialize(), favorite_character))

    favorite_planet = FavoritesPlanets.query.all()
    planet_favorite = list(map(lambda item: item.serialize(), favorite_planet))

    favorite_vehicle = FavoritesVehicles.query.all()
    vehicle_favorite = list(map(lambda item: item.serialize(), favorite_vehicle))

    if character_favorite == [] and planet_favorite == [] and vehicle_favorite == []:
        return jsonify({"msg":"Empty"}), 404  

    response_body = {
        "msg": "Ok",
        "result": [
            character_favorite, 
            planet_favorite, 
            vehicle_favorite
        ]
    }

    return jsonify(response_body), 200


#Endpoint Todos los Personajes------------------------------------------------------------------------------------------
@app.route('/people', methods=['GET'])
def get_all_people():

    query_results = Characters.query.all()
    results = list(map(lambda item: item.serialize(), query_results))
    # print(results)
    if results == []:
        return jsonify({"msg":"Empty"}), 404

    response_body = {
        "msg": "Ok",
        "result": results
    }

    return jsonify(response_body), 200

#Endpoint Get one Character--------------------------------------------------------------------------------------------
@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_people(people_id):
    # this is how you can use the Family datastructure by calling its methods
    character = Characters.query.get(people_id)
    if character is None:
        return jsonify({"msg": "No existe el personaje"}), 404
    return jsonify(character.serialize()), 200

#Enpoint POST añadir personaje a favoritos--------------------------------------------------------------------------------
@app.route('/favorite/people/<int:id>', methods=['POST'])
def create_favorite_people(id):
    # this is how you can use the Family datastructure by calling its methods
    body = request.json
    print(body)

    check_user = User.query.filter_by(id=body["id"]).first()
    people_exist = Characters.query.filter_by(id=id).first()

    if people_exist is None:
        return jsonify({"msg":"Character not exist"}), 404
    else:
        if check_user is None:
            return jsonify({"msg":"User don't exist"}), 404
        else:
            check_favorite_people = FavoritesCharacters.query.filter_by(id=id, user_id=body["id"]).first()
            if check_favorite_people is None:
                new_favorite_people = FavoritesCharacters(user_id=body["id"], id=id)
                db.session.add(new_favorite_people)
                db.session.commit()
                return jsonify({"msg":"Favorite character added"}), 200
            else:
                return jsonify({"msg":"Favorite character already exists"}), 400
            
#Enpoint DELETE personaje de favoritos--------------------------------------------------------------------------------
@app.route('/favorite/people/<int:id>', methods=['DELETE'])
def delete_favorite_people(id):
    
    del_favorite_character = FavoritesCharacters.query.filter_by(id=id).first()
    print(del_favorite_character)
    
    if del_favorite_character is None:
        return jsonify({"msg":"Favorite character don't exist"}), 404
    else:
        # delete_favorite_people = FavoritesCharacters(id=id, user_id=["id"])
        db.session.delete(del_favorite_character)
        db.session.commit()
    return jsonify({"msg":"Favorite character deleted"}), 200

#Endpoint ALL Planets--------------------------------------------------------------------------------------------------
@app.route('/planets', methods=['GET'])
def get_all_planets():

    query_results = Planets.query.all()
    results = list(map(lambda item: item.serialize(), query_results))
    # print(results)
    if results == []:
        return jsonify({"msg":"Empty"}), 404

    response_body = {
        "msg": "Ok",
        "result": results
    }

    return jsonify(response_body), 200


#Endpoint Get one Planet-----------------------------------------------------------------------------
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    # this is how you can use the Family datastructure by calling its methods
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "No existe el planeta"}), 404
    return jsonify(planet.serialize()), 200
    

#Enpoint POST añadir planeta a favoritos-----------------------------------------------------------------
@app.route('/favorite/planets/<int:id>', methods=['POST'])
def create_favorite_planet(id):
    # this is how you can use the Family datastructure by calling its methods
    body = request.json

    check_user = User.query.filter_by(id=body["id"]).first()
    planet_exist = Planets.query.filter_by(id=id).first()

    # if check_user and planet_exist is None:
    #     return jsonify({"msg":"planet and user don't exist"}), 404
    # else:
    if planet_exist is None:
        return jsonify({"msg":"Planet not exist"}), 404
    else:
        if check_user is None:
            return jsonify({"msg":"User don't exist"}), 404
        else:
            check_favorite_planet = FavoritesPlanets.query.filter_by(planets_id=id, user_id=body["id"]).first()
            if check_favorite_planet is None:
                new_favorite_planet = FavoritesPlanets(user_id=body["id"], planets_id=id)
                db.session.add(new_favorite_planet)
                db.session.commit()
                return jsonify({"msg":"Favorite planet added"}), 200
            else:
                return jsonify({"msg":"Favorite planet already exists"}), 400

#Enpoint DELETE planeta de favoritos--------------------------------------------------------------------------------
@app.route('/favorite/planet/<int:id>', methods=['DELETE'])
def delete_favorite_planet(id):
    
    del_favorite_planet = FavoritesPlanets.query.filter_by(id=id).first()
    print(del_favorite_planet)
    
    if del_favorite_planet is None:
        return jsonify({"msg":"Favorite planet don't exist"}), 404
    else:
        # delete_favorite_people = FavoritesCharacters(id=id, user_id=["id"])
        db.session.delete(del_favorite_planet)
        db.session.commit()
    return jsonify({"msg":"Favorite planet deleted"}), 200



#Endpoint ALL Vehicles----------------------------------------------------------------------------------
@app.route('/vehicles', methods=['GET'])
def get_all_vehicles():

    query_results = Vehicles.query.all()
    results = list(map(lambda item: item.serialize(), query_results))
    # print(results)
    if results == []:
        return jsonify({"msg":"Empty"}), 404

    response_body = {
        "msg": "Ok",
        "result": results
    }

    return jsonify(response_body), 200


#Endpoint Get one Vehicle--------------------------------------------------------------------------------
@app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_one_vehicle(vehicle_id):
    # this is how you can use the Family datastructure by calling its methods
    vehicle = Vehicles.query.get(vehicle_id)
    if vehicle is None:
        return jsonify({"msg": "No existe el vehiculo"}), 404
    return jsonify(vehicle.serialize()), 200

#Enpoint POST añadir vehiculo a favoritos-------------------------------------------------------------------
@app.route('/favorite/vehicles/<int:id>', methods=['POST'])
def create_favorite_vehicle(id):
    # this is how you can use the Family datastructure by calling its methods
    body = request.json
    print(body)

    check_user = User.query.filter_by(id=body["id"]).first()
    vehicle_exist = Vehicles.query.filter_by(id=id).first()

    # if check_user and vehicle_exist is None:
    #     return jsonify({"msg":"Vehicle and user don't exist"}), 404
    # else:
    if vehicle_exist is None:
        return jsonify({"msg":"Vehicle not exist"}), 404
    else:
        if check_user is None:
            return jsonify({"msg":"User don't exist"}), 404
        else:
            check_favorite_vehicle = FavoritesVehicles.query.filter_by(vehicles_id=id, user_id=body["id"]).first()
            if check_favorite_vehicle is None:
                new_favorite_vehicle = FavoritesVehicles(user_id=body["id"], vehicles_id=id)
                db.session.add(new_favorite_vehicle)
                db.session.commit()
                return jsonify({"msg":"Favorite vehicle added"}), 200
            else:
                return jsonify({"msg":"Favorite vehicle already exists"}), 400
            

#Enpoint DELETE vehiculo de favoritos--------------------------------------------------------------------------------
@app.route('/favorite/vehicle/<int:id>', methods=['DELETE'])
def delete_favorite_vehicle(id):
    
    del_favorite_vehicle = FavoritesVehicles.query.filter_by(id=id).first()
    print(del_favorite_vehicle)
    
    if del_favorite_vehicle is None:
        return jsonify({"msg":"Favorite vehicle don't exist"}), 404
    else:
        # delete_favorite_people = FavoritesCharacters(id=id, user_id=["id"])
        db.session.delete(del_favorite_vehicle)
        db.session.commit()
    return jsonify({"msg":"Favorite vehicle deleted"}), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
