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


# db_drop_and_create_all(app)

# ROUTES

@app.route('/drinks')
def getDrinks():
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def getDrinkDetails(jwt):
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def createDrink(body):
    try:
        body = request.get_json()
        new_drink = Drink(title=body['title'],
                          recipe=json.dumps(body['recipe']))
        Drink.insert(new_drink)

        return jsonify({
            'success': True,
            'drinks': [Drink.long(new_drink)]
        }), 200

    except:
        abort(400)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def updateDrinks(payload, id):
    try:
        body = request.get_json()
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if not drink:
            abort(404)

        drink.title = body['title']
        drink.recipe = json.dumps(body['recipe'])
        Drink.update(drink)

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    except:
        abort(403)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def deleteDrink(payload, id):

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    try:
        Drink.delete(drink)
        return jsonify({
            'success': True,
            'deleted_drink': id
        }), 200

    except:
        abort(422)

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(AuthError)
def auth_error(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error
    }), auth_error.status_code


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


if __name__ == "__main__":
    app.run(debug=True)
