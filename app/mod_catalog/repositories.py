# The repository is an object that hides the details
# of persistent storage by presenting us with an interface
# that looks like a collection


from app.mod_catalog.models import Category, CatalogItem, CatalogImage

# To get the current date
from datetime import datetime

# built-in function for SQL query
from sqlalchemy import desc, func


class RepositoryBase:
    def __init__(self, db_session):
        self.session = db_session

    def commit(self):
        self.session.commit()


class CategoryRepository(RepositoryBase):
    """
    Category object-oriented view of the persistence layer
    """

    def __init__(self, session_db):
        RepositoryBase.__init__(self, session_db)

    def find_by_name(self, category_name):
        return Category.query.  \
            filter_by(name=category_name). \
            one_or_none()

    def all(self, column_order=Category.id):
        return Category.query. \
            order_by(column_order). \
            all()

    def add(self, category):
        self.add(category)

    def add_all(self, categories):
        for category in categories:
            self.session.add(category)

    def delete(self, category):
        self.session.delete(category)

    def count(self):
        return self.session. \
            query(func.count(Category.id)). \
            one_or_none()[0]


class CatalogItemRepository(RepositoryBase):
    """
    CatalogItem object-oriented view of the persistence layer
    """

    def __init__(self, session_db):
        RepositoryBase.__init__(self, session_db)

    def get_lasteds(self):
        """
        Get catalog items by number categories
        """
        num_categories = CategoryRepository(self.session). \
            count()
        return CatalogItem.query. \
            order_by(desc(CatalogItem.id)). \
            limit(num_categories). \
            all()

    def get_by_category_name(self, category_name):
        return CatalogItem.query. \
            join(CatalogItem.category). \
            filter(Category.name == category_name)

    def find(self, id):
        return CatalogItem.query. \
            filter_by(id=id). \
            one_or_none()

    def find_by_title(self, title):
        return CatalogItem.query. \
            filter_by(title=title). \
            one_or_none()

    def find_by_category_name_and_title(self, category_name, catalog_title):
        return CatalogItem.query. \
            filter(Category.name == category_name,
                   CatalogItem.title == catalog_title). \
            one_or_none()

    def has_item_by_title(self, title):
        return CatalogItem.query. \
            filter(CatalogItem.title == title). \
            count() > 0

    def add_with_date(self, catalog_item):
        """
        Add catalog item with a current date time
        """
        catalog_item.date = datetime.now()
        self.add(catalog_item)

    def add(self, catalog_item):
        self.session.add(catalog_item)

    def delete(self, catalog_item):
        self.session.delete(catalog_item)
