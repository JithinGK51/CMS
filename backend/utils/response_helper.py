from flask import jsonify

def success_response(message="Success", data=None):
    return jsonify({
        "success": True,
        "message": message,
        "data": data or {}
    }), 200

def error_response(message="Error", code=400):
    return jsonify({
        "success": False,
        "message": message,
        "data": {}
    }), code
