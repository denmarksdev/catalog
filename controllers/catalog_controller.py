from flask import Blueprint, render_template, request, redirect, url_for, flash
from data.database_setup import CatalogItem, CatalogImage
from data.data_access import UserDao, CatalogItemDao, CategoryDao
from controllers.auth_controller import login_session, is_logged
from constants import IMAGE_PATH
import requests
# File managment
from os import remove as remove_file
from os.path import exists as files_exists

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
    category_dao = CategoryDao()
    item_dao = CatalogItemDao()

    item = item_dao.find_by_category_name_and_title(category_name, item_title)
    image_url = get_url_image(item.image)
    categories = category_dao.get_all()

    # Verify the user can edit CatalogItem
    is_owner = is_logged() and (item.user_id == login_session['user_id'])

    print(is_logged())

    print(login_session)

    # Search the author of catalog item
    author_name = ""
    if (not is_owner):
        user_dao = UserDao()
        author = user_dao.find(item.user_id)
        author_name = author.name

    return render_template('catalog-item-detail.html',
                           categories=categories,
                           item=item,
                           is_owner=is_owner,
                           author_name=author_name,
                           image_url=image_url)


@catalog_controller.route('/<string:category_name>/<string:item_title>/edit', methods=['GET', 'POST'])
def edit_item(category_name, item_title):
    category_dao = CategoryDao()
    item_dao = CatalogItemDao()

    if (not is_logged()):
        return redirect(url_for('show_login'))

    if (request.method == 'GET'):
        categories = category_dao.get_all()
        item = item_dao.find_by_category_name_and_title(category_name,
                                                        item_title)

        return render_template('catalog-item-edit.html',
                               category_name=category_name,
                               categories=categories,
                               item=item,
                               action="/catalog/%s/%s/edit" % (
                                   category_name, item_title),
                               url_image=get_url_image(item.image))
    else:  # POST
        catalog_id = int(request.form['catalog_id'])
        item = item_dao.find(catalog_id)
        set_item_info(item, request.form, )
        item_dao.save(item)

        # Check image is saved on database
        item = item_dao.find(item.id)
        if (item.image):
            # Save image from file
            image_file = bytearray(item.image.data)
            file_image = open(IMAGE_PATH + item.image.get_name(), "w+")
            file_image.write(item.image.data)

        return redirect(url_for('catalog.show_catalog'))


@catalog_controller.route('/<string:category_name>/<string:item_title>/delete', methods=['GET', 'POST'])
def delete_item(category_name, item_title):
    dao = CatalogItemDao()

    if (not is_logged()):
        return redirect(url_for('show_login'))

    item = dao.find_by_title(item_title)

    if (request.method == 'GET'):
        return render_template('catalog-item-delete.html',
                               item=item,
                               url_image=get_url_image(item.image))
    elif (request.method == 'POST'):
        # Removes the image file from the server
        image_path = IMAGE_PATH + item.image.get_name()
        if (item.image and files_exists(image_path)):
            remove_file(IMAGE_PATH + item.image.get_name())

        dao.delete(item)
        return redirect(url_for('catalog.show_catalog'))


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
