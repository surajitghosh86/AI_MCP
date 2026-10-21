import json

import pyodbc
from flask import Flask, jsonify, request

try:
    from dbHelper_sp import ItemDatabase
except ImportError:
    from py_ApiWithSqlDb.dbHelper_sp import ItemDatabase

app = Flask(__name__)

db = ItemDatabase()


def _db_error_response(ex: pyodbc.Error):
    return jsonify({"message": "Database error", "error": str(ex)}), 500


@app.route("/getCustomers", methods=["GET"])
def getCustomers():
    try:
        return jsonify(db.getCustomers()), 200
    except pyodbc.Error as ex:
        return _db_error_response(ex)


@app.route("/getCustomer/<int:id>", methods=["GET"])
def getCustomer(id):
    try:
        customer = db.getCustomer(id)
        if customer:
            return jsonify(customer), 200
        return jsonify({"message": "Customer not found"}), 404
    except pyodbc.Error as ex:
        return _db_error_response(ex)


@app.route("/createCustomer", methods=["POST"])
def createCustomer():
    try:
        if not request.is_json:
            return jsonify({"message": "Request must be JSON"}), 400

        data = request.get_json()
        if not data or "FirstName" not in data or "LastName" not in data:
            return jsonify({"message": "FirstName and LastName are required"}), 400

        return jsonify(db.createCustomer(data)), 201
    except pyodbc.Error as ex:
        return _db_error_response(ex)


@app.route("/updateCustomer/<int:id>", methods=["PUT"])
def updateCustomer(id):
    try:
        if not request.is_json:
            return jsonify({"message": "Request must be JSON"}), 400

        data = request.get_json()
        if not data or "FirstName" not in data or "LastName" not in data:
            return jsonify({"message": "FirstName and LastName are required"}), 400

        result = db.updateCustomer(id, data)
        if result.get("message") == "Data not found":
            return jsonify({"message": "Customer not found"}), 404
        return jsonify(result), 200
    except pyodbc.Error as ex:
        return _db_error_response(ex)


@app.route("/deleteCustomer/<int:id>", methods=["DELETE"])
def deleteCustomer(id):
    try:
        result = db.deleteCustomer(id)
        if result.get("message") == "Data not found":
            return jsonify({"message": "Customer not found"}), 404
        return jsonify(result), 200
    except pyodbc.Error as ex:
        return _db_error_response(ex)


if __name__ == "__main__":
    app.run(debug=True)
