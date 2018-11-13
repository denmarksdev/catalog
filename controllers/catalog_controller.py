from flask import Blueprint, render_template, request, redirect, url_for, flash
from data.database_setup import CatalogItem, CatalogImage
from data.data_access import CatalogItemDao, CategoryDao
from controllers.auth_controller import login_session, is_logged
from constants import IMAGE_PATH
import requests


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


@catalog_controller.route('/add-item', methods=['GET', 'POST'])
def add_item():
    category_dao = CategoryDao()
    item_dao = CatalogItemDao()

    if (not is_logged()):
        return redirect(url_for('auth_controller_pages.show_login'))

    item = CatalogItem(title='', description='')

    if (request.method == 'GET'):
        categories = category_dao.get_all()
        return render_template('catalog-item-edit.html',
                               categories=categories,
                               item=item,
                               action="/catalog/add-item",
                               url_image="/" + IMAGE_PATH + "default.png")
    else:  # POST
        set_item_info(item, request.form, is_add_action=True)

        hasItem = item_dao.has_item_by_title(item.title)
        if (hasItem):
            categories = category_dao.get_all()
            flash("Title '%s' is already registered" % item.title)
            return render_template('catalog-item-edit.html',
                                   categories=categories,
                                   item=item,
                                   action="/catalog/add-item")

        item_dao.insert(item)

        if (item.image):
            # Save image from file
            item = item_dao.find_by_title(item.title)
            image_file = bytearray(item.image.data)
            file_image = open(IMAGE_PATH + item.image.get_name(), "w+")
            file_image.write(item.image.data)

        return redirect(url_for('catalog.show_catalog'))


@catalog_controller.route('/<string:category_name>/<string:item_title>')
def catalog_show_item_details(category_name, item_title):
    return "Catalog Item Details page"


@catalog_controller.route('/<string:category_name>/<string:item_title>/edit', methods=['GET', 'POST'])
def edit_item(category_name, item_title):
    return "Edit Catalog item page"


@catalog_controller.route('/<string:category_name>/<string:item_title>/edit', methods=['GET', 'POST'])
def delete_item(category_name, item_title):
    return "Delete Catalog item page"


# Auxiliary Functions

def set_item_info(item, form_data, is_add_action=False):
    """
    Fill CatalogItem with form data information
    """
    item.title = form_data['title']
    item.description = form_data['description']
    item.category_id = int(form_data['category_id'])
    item.user_id = int(login_session['user_id'])

    if (is_add_action):
        item.image = CatalogImage()

    # Define image for CatalogItem
    if (request.files and request.files['image']):
        file = request.files['image']
        item.image.suffix = file.mimetype.replace('image/', '')
        item.image.data = file.read()
    elif(is_add_action):  # Add image only Add Form operation
        file = open(IMAGE_PATH + "default.png")
        item.image.suffix = "png"
        item.image.data = file.read()


def get_url_image(image):
    """
    Get Url Image for CatalogImagem Item on the server
    """
    return "http://localhost:8080/" + IMAGE_PATH + image.get_name()
