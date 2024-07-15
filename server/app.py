#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api=Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers = Camper.query.all()
        campers_dict = []
        for camper in campers:
            campers_dict.append(camper.to_dict_2())
        response = make_response(campers_dict, 200)
        return response

    def post(self):
        json_data = request.get_json()
        if json_data.get('age') < 8 or json_data.get('age') > 18 or not json_data.get('name'):
            return { "errors": ["validation errors"] }, 400

        new_record = Camper(
            name=json_data.get('name'),
            age=json_data.get('age')
        )
        db.session.add(new_record)
        db.session.commit()
        if not new_record.id:
            return { "errors": ["validation errors"] }, 400
        return make_response(new_record.to_dict(), 201)

class CampersById(Resource):
    def get(self, id):
        camper = Camper.query.filter(Camper.id==id).first()
        if not camper:
            return {"error": "Camper not found"}, 404

        return make_response(camper.to_dict(), 202)

    def patch(self, id):
        camper = Camper.query.filter(Camper.id==id).first()
        print(camper)
        if not camper: 
            return {"error": "Camper not found"},404
        json_data = request.get_json()
        name = json_data.get('name').replace('(updated)','')
        if json_data.get('age') < 8 or json_data.get('age') > 18 or not json_data.get('name'):
            return { "errors": ["validation errors"] }, 400
        if 'name' in json_data:
            camper.name=name
        if 'age' in json_data:
            camper.age=json_data.get('age')

        db.session.add(camper)
        db.session.commit()
    
        return make_response(camper.to_dict_2(), 202)

class Activities(Resource):
    def get(self):
        activities = Activity.query.all()
        activities_dict = []
        for activity in activities:
            activities_dict.append(activity.to_dict())
        return activities_dict, 200

class ActivityById(Resource):
    def delete(self, id):
        record = Activity.query.filter(Activity.id==id).first()
        if not record:
            return {"error": "Activity not found"}, 404
        db.session.delete(record)
        db.session.commit()

        return {} , 204

class Signups(Resource):
    def post(self):
        json_data = request.get_json()
        if json_data.get('time') < 0 or json_data.get('time') > 23:
            return {'errors': ["validation errors"]}, 400
        rew_record = Signup(
            camper_id=json_data.get('camper_id'),
            activity_id=json_data.get('activity_id'),
            time=json_data.get('time')
        )
        db.session.add(rew_record)
        db.session.commit()
        return make_response(rew_record.to_dict(), 201)

api.add_resource(Campers, '/campers')
api.add_resource(CampersById,'/campers/<int:id>')
api.add_resource(Activities, '/activities')
api.add_resource(ActivityById, '/activities/<int:id>')
api.add_resource(Signups,'/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
