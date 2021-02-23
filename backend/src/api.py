import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


## ROUTES
@app.route('/drinks')
def show_drinks():
    drinks = Drink.query.all()
    drinks_list = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': drinks_list
    })


'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:details')
def show_drinks_detail():
    drinks = Drink.query.all()
    drinks_list = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': drinks_list
    })


'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    title = request.get_json()['title']
    recipe = request.get_json()['recipe']
    if title==None or recipe==None:
        abort(422)
    try:
        new_drink = Drink()
        new_drink.title = title
        new_drink.recipe = json.dumps(recipe)
        new_drink.insert()
        return jsonify({
                        'status': 200,
                        'success':True,
                        'drink_id': new_drink.id
                        })
    except Exception as e:
        abort(422)


'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drink')
def update_drink_details(drink_id):
    drink = Drink.query.get(drink_id)
    title = request.get_json()['title']
    if title==None:
        abort(422)
    try:
        drink.title = title
        drink.update()
        return jsonify({
                        'success':True,
                        'status': 200,
                        'drink_id': drink.id
                        })
    except Exception as e:
        abort(422)


'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks_item(drink_id):
    drink = Drink.query.get(drink_id)
    if drink == None:
        abort(422)
    try:
        drink.delete()
        return jsonify({
            'success': True,
            'status': 200,
            'drink_id':drink_id
        })
    except:
        abort(422)


## Error Handling
'''
Example error handling: UnAuthentic Request
'''
@app.errorhandler(401)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "the resource not found"
                    }), 401


'''
Example error handling: UnAuthorized User
'''
@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 'Authentication Error make sure you use valid token'
    })


'''
Example error handling: UnAuthentic user
'''
@app.errorhandler(403)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 403,
                    "message": "the resource not found"
                    }), 403


'''
Example error handling for Not found resources
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "the resource not found"
                    }), 404


'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422