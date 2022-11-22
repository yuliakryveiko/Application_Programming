from flask import  jsonify, make_response


def StatusResponse(response, code):
    end_response = make_response(jsonify(response = response,code = code),code)
    return end_response
