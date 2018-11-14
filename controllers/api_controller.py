from flask import Blueprint, jsonify, make_response
from data.data_access import CategoryDao, CatalogItemDao
from constants import BASE_API_URL

api_controller = Blueprint('api_controller',
                           __name__,
                           url_prefix=BASE_API_URL)


@api_controller.route("/catalog.json")
def get_catalog():
    """
    Returns a JSON with all categories and their respective Catalog Item.
    """
    dao = CategoryDao()
    categories = dao.get_all()
    return jsonify(Category=[c.serialize_with_catalog_items for c in categories])


@api_controller.route("/item/<string:title>")
def get_catalog_item(title):
    dao = CatalogItemDao()
    itemCatalog = dao.find_by_title(title)
    if (itemCatalog == None):
        return make_response("Catalog Item %s not found" % title, 404)

    return jsonify(Item=itemCatalog.serialize)
