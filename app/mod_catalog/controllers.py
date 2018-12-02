# Import flask dependencies
from flask import Blueprint, request, render_template, \
    flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db
from app.unit_of_work import CatalogUnitOfWork
from app.mod_catalog.repositories import CatalogItemRepository
from config import PUBLIC_URL, IMAGE_DIR

# Authentication session information
from app.mod_auth.helpers import login_session, \
    is_logged, is_item_owner

# Define the blueprint: 'catalog', set its url prefix: app.url/catalog
mod_catalog = Blueprint('catalog', __name__, url_prefix='/catalog')

# Build Catalog Item form with WTForms
from app.mod_catalog.models import Category, \
    CatalogItem, CatalogImage
from app.mod_catalog.forms import ItemForm, ItemDeleteForm
from werkzeug.datastructures import CombinedMultiDict

# File managment
from config import IMAGE_URL_BASE, IMAGE_DIR
from os import remove as remove_file
from os.path import exists as files_exists


@mod_catalog.route('/')
def show():
    """
    Show Catalog Items for each category
    """
    uow = CatalogUnitOfWork(db.session)

    categories = uow.categories.all()
    lasted_items = uow.catalog_items.get_lasteds()

    return render_template('catalog/index.html',
                           categories=categories,
                           lastedItems=lasted_items)


@mod_catalog.route('/<string:category_name>/items')
def show_items(category_name):
    """
    Show Catalog Items by category name
    """
    uow = CatalogUnitOfWork(db.session)

    categories = uow.categories.all()
    items = uow.catalog_items.get_by_category_name(category_name)

    return render_template('catalog/items.html',
                           category_name=category_name,
                           categories=categories,
                           items=items)


@mod_catalog.route('/<string:category_name>/<string:item_title>')
def show_details(category_name, item_title):
    """
    Show Catalog Item details
    """
    uow = CatalogUnitOfWork(db.session)

    categories = uow.categories.all()
    # Catalog Item Informations
    item = uow.catalog_items. \
        find_by_category_name_and_title(category_name, item_title)
    img_url = item.image.get_url(PUBLIC_URL)

    # check if the user can edit the item
    is_owner = is_item_owner(item.user_id)

    # Search the author of catalog item
    author_name = ""
    if (not is_owner):
        author = uow.users.find(item.user_id)
        author_name = author.name

    return render_template('catalog/item-detail.html',
                           categories=categories,
                           item=item,
                           is_owner=is_owner,
                           author_name=author_name,
                           image_url=img_url)


@mod_catalog.route('/add-item', methods=['GET', 'POST'])
def add_item():
    """
    Add new Catalog Item
    """
    if (not is_logged()):
        return redirect(url_for('auth.show_signin'))

    uow = CatalogUnitOfWork(db.session)

    # Create New user
    item = CatalogItem(title='', description='')

    # If Item Catalog in form is submitted
    form = ItemForm(CombinedMultiDict((request.files, request.form)))
    categories = uow.categories.all(column_order=Category.name)
    form.setCategories(categories)

    # Verify the sign in form
    if form.validate_on_submit():
        set_item_info(item, form, is_add_action=True)
        hasItem = uow.catalog_items.has_item_by_title(item.title)
        if (hasItem):
            flash("Title '%s' is already registered" % item.title)
        else:  # Persist Catalog Item
            uow.catalog_items.add_with_date(item)
            uow.commit()
            # Save image file from database
            if (item.image):
                item = uow.catalog_items.find_by_title(item.title)
                save_image_file(item.image)

            return redirect(url_for('catalog.show'))

    # GET Request
    return render_template('catalog/item-edit.html',
                           categories=categories,
                           form=form,
                           action=url_for('catalog.add_item'),
                           url_image=IMAGE_URL_BASE + "/default.png")


@mod_catalog.route('/<string:category_name>/<string:item_title>/edit',
                   methods=['GET', 'POST'])
def edit_item(category_name, item_title):
    """
    Edit the Catalog Item
    """
    if (not is_logged()):
        return redirect(url_for('auth.show_signin'))

    uow = CatalogUnitOfWork(db.session)

    # Find user
    item = uow.catalog_items. \
        find_by_category_name_and_title(category_name, item_title)

    if (not item):
        flash("Catalog Item '%s' not exists" % item_title)
        return redirect(url_for('catalog.show'))
    if (not is_item_owner(item.user_id)):
        flash("Catalog Item '%s' is not create for user" % item_title)
        return redirect(url_for('catalog.show'))

    categories = uow.categories.all(column_order=Category.name)

    # If Item Catalog in form is submitted
    form = ItemForm(CombinedMultiDict((request.files, request.form)))
    form.setCategories(categories)

    has_error = False

    # Verify the sign in form
    if form.validate_on_submit():
        set_item_info(item, form)
        # Check if another item name is already registered
        # Check whether the previous and deferential title of the first
        title_is_different = (item_title != item.title)
        has_item = uow.catalog_items.has_item_by_title(item.title)
        if (title_is_different and has_item):
            flash("Title '%s' is already registered" % item.title)
            uow.rollback()
            has_error = True
        else:
            # Persist Catalog Item
            uow.catalog_items.add(item)
            uow.commit()
            # Save image file from database
            if (item.image):
                item = uow.catalog_items.find_by_title(item.title)
                save_image_file(item.image)
            return redirect(url_for('catalog.show'))

    # GET Request

    # keep the form if the form have validation errors in the POST
    if (not has_error):
        # Fill the forms fields
        form.title.data = item.title
        form.description.data = item.description
        form.categories.data = item.category_id

    url_action = url_for('catalog.edit_item',
                         category_name=category_name,
                         item_title=item_title)

    return render_template('catalog/item-edit.html',
                           categories=categories,
                           form=form,
                           action=url_action,
                           url_image=item.image.get_url(PUBLIC_URL))


@mod_catalog.route('/<string:category_name>/<string:item_title>/delete',
                   methods=['GET', 'POST'])
def delete_item(category_name, item_title):
    """
    Delete the Catalog Item
    """
    repo = CatalogItemRepository(db.session)

    if (not is_logged()):
        return redirect(url_for('show_login'))

    item = repo.find_by_title(item_title)
    url_image = item.image.get_url(PUBLIC_URL)

    form = ItemDeleteForm(request.form)
    if (form.validate_on_submit):
        if item.image:
            delete_image_file(item.image)
        repo.delete(item)
        repo.commit()
        return redirect(url_for('catalog.show'))

    # GET
    return render_template('catalog/item-delete.html',
                           item=item,
                           url_image=url_image)


# Auxiliary Functions

def set_item_info(item, form, is_add_action=False):
    """
    Fill Catalog Item with form data 
    """
    item.title = form.title.data
    item.description = form.description.data
    item.category_id = form.categories.data
    item.user_id = int(login_session['user_id'])

    if (is_add_action):
        item.image = CatalogImage()

    # Define image for CatalogItem
    if (form.image.data):
        file = form.image.data
        item.image.suffix = file.mimetype.replace('image/', '')
        item.image.data = file.read()
    elif(is_add_action):  # Add image only on Add Form operation
        file = open(IMAGE_DIR + '/default.png')
        item.image.suffix = "png"
        item.image.data = file.read()


def save_image_file(image):
    "Save Catalog Item Image file from Largebinary"
    image_path = IMAGE_DIR + "/" + image.get_name()
    file_image = open(image_path, "w+")
    file_image.write(image.data)


def delete_image_file(image):
    image_path = IMAGE_DIR + "/" + image.get_name()
    if (files_exists(image_path)):
        remove_file(image_path)
