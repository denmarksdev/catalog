from flask import Blueprint
from constants import BASE_API_URL

api_controller = Blueprint('api_controller',
                           __name__,
                           url_prefix=BASE_API_URL)


@api_controller.route("/catalog.json")
def get_catalog():
    """
    Returns a JSON with all categories and their respective Catalog Item.
    """
    return  "CATALOG JSON"


@api_controller.route("/item/<string:item_name>")
def get_catalog_item(item_name):
    """
    Returns a JSON with all categories and their respective Catalog Item.
    """
    return "ITEM JSON"
