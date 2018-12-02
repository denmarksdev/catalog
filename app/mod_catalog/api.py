from flask import Blueprint, make_response, jsonify
from flask_restful import Resource, Api
from config import API_URL
from app import db
from app.mod_catalog.repositories import CategoryRepository, \
    CatalogItemRepository

api_controller = Blueprint('api_catalog',
                           __name__,
                           url_prefix=API_URL)

# Link an Api up to a Blueprint.
api = Api(api_controller)

class CatalogResource(Resource):
    """
    Returns a JSON with all categories and their respective Catalog Item.
    """

    def get(self):
        repo = CategoryRepository(db.session)
        categories = repo.all()
        return jsonify(Category=[c.serialize_with_catalog_items
                                 for c in categories])


class CatalogItemResource(Resource):
    """
    Return Catalog Item by title
    """

    def get(self, title):
        repo = CatalogItemRepository(db.session)
        itemCatalog = repo.find_by_title(title)
        if (itemCatalog is None):
            return make_response("Catalog Item %s not found" % title, 404)
        return jsonify(Item=itemCatalog.serialize)


# Register apis on blueprint
api.add_resource(CatalogResource, '/catalog.json')
api.add_resource(CatalogItemResource, '/catalog.json/<string:title>')
