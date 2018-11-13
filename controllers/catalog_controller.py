from flask import Blueprint, render_template
from data.data_access import CatalogItemDao, CategoryDao

catalog_controller = Blueprint('catalog',
                               __name__,
                               url_prefix='/catalog',
                               template_folder='templates',
                               static_url_path='/static')
# Endpoints


@catalog_controller.route('/')
def show_catalog():
    category_dao = CategoryDao()
    item_dao = CatalogItemDao()

    lastedItems = item_dao.get_lasteds()
    categories = category_dao.get_all()
    return render_template('catalog.html',
                           categories=categories,
                           lastedItems=lastedItems)


@catalog_controller.route('/<string:category_name>/items')
def show_items_by_category(category_name):
    category_dao = CategoryDao()
    item_dao = CatalogItemDao()

    categories = category_dao.get_all()
    items = item_dao.get_by_category_name(category_name)
    return render_template('catalog-items.html',
                           category_name=category_name,
                           categories=categories,
                           items=items)


@catalog_controller.route('/<string:category_name>/<string:item_title>')
def catalog_show_item_details(category_name, item_title):
    return "Catalog Item Details page"


@catalog_controller.route('/add-item', methods=['GET', 'POST'])
def add_item():
    return "Add CatalogItem page"


@catalog_controller.route('/<string:category_name>/<string:item_title>/edit', methods=['GET', 'POST'])
def edit_item(category_name, item_title):
    return "Edit Catalog item page"


@catalog_controller.route('/<string:category_name>/<string:item_title>/edit', methods=['GET', 'POST'])
def delete_item(category_name, item_title):
    return "Delete Catalog item page"
