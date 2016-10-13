from app.exceptions import JsonOutputException
from flask import request

from . import api_blueprint
from app.models import Region

@api_blueprint.route('/province/')
def province():
    provinces = Region.get_province()
    return {
        'data': provinces
    }

@api_blueprint.route('/city/')
def city():
    pro_id = request.args.get('pro_id')
    if not pro_id:
        raise JsonOutputException('need pro_id')
    cities = Region.get_city(pro_id)
    return {
        'data': cities
    }

@api_blueprint.route('/area/')
def area():
    city_id = request.args.get('city_id')
    if not city_id:
        raise JsonOutputException('need city_id')
    areas = Region.get_area(city_id)
    return {
        'data': areas
    }