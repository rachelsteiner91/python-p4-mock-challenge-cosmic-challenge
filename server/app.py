#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Planet, Scientist, Mission

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api=Api(app)

@app.route('/')
def home():
    return ''

##~~~~~~SCIENTISTS ROUTES~~~~~~##
##GET /scientists
class Scientists(Resource):
    def get(self):
        # scientists=Scientist.query.all()
        scientists=[scientist.to_dict() for scientist in Scientist.query.all()] ## this combines the steps into one, each space in the list is occupied by a scientist
        
        return scientists, 200
##POST /scientists
    def post(self):
        data = request.get_json()
        new_scientist = Scientist(
            name = data.get('name'),
            field_of_study=data.get('field_of_study'),
            avatar=data.get('avatar'),
        )
        try:
            db.session.add(new_scientist)
            db.session.commit()
            return new_scientist.to_dict(), 201
        except ValueError:
            return ({'error': '400: Validation error'}, 400)


##~~~~~~SCIENTISTSBYID ROUTES~~~~~~##
##GET /scientists/int:id
##If the Scientist does not exist, return the following JSON data, along with the appropriate HTTP status code: 404
##remember: the Scientist model name cannot be used as a name
class ScientistsByID(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return ({'Error' : '404: Scientist not found'})
        return scientist.to_dict(
            only=(
                'id',
                'name',
                'field_of_study',
                'avatar',
                'planets',
                '-planets.missions',
                )
            )  
##PATCH /scientists/:id
    def patch(self, id):
        data=request.get_json()
        scientist = Scientist.query.query.filter_by(Scientist.id==id).first()
        if not scientist:
            return ({'error': '404: Scientist not found'}, 404)
        for attr in data:
            setattr(scientist, attr, data.get(attr))
        try:
            db.session.add(scientist)
            db.session.commit()
            return (scientist.to_dict(
                only=('id', 'name', 'field_of_study', 'avatar')
                ), 
                202, 
                )
        except:
            return {'error': '400: Validation'}, 400
    
##DELETE /scientists/int:id
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id ==id).first()
        if not scientist:
            return ({'error': '404: Scientist not found'}, 404)
        missions = Mission.query.filter(
            Mission.scientist_id == scientist.id
        ).all()
        for mission in missions:
            db.session.delete(mission)
            db.session.commit()
        db.session.delete(scientist)
        db.session.commit()
        return ({}, 204)

##~~~~~~PLANETS ROUTES~~~~~~##
## GET /planets
class Planets(Resource):
    def get(self):
        return [planet.to_dict() for planet in Planet.query.all()], 200


##~~~~~~MISSIONS ROUTES~~~~~~##
##POST /missions     
class Missions(Resource):
    def get(self):
        missions = [mission.to_dict() for mission in Mission.query.all()]
        return (missions, 200)
    def post(self):
        data=request.get_json()
        new_mission=Mission(
            name=data.get('name'), 
            scientist_id=data.get('scientist.id'), 
            planet_id=data.get('planet_id')
            )
        try:
            db.session.add(new_mission)
            db.session.commit()
            return (new_mission.to_dict, 201)
        except:
            return ({'error': '400:Validation error'}, 400)

api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistsByID, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)

##DEBUG
    ## >>>> Mission(name="hello", scientist_id=4, planet_id=1)
    ## >>>>db.session.add(mission)
    ## >>>>db.session.commit()
