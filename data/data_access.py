from datetime import datetime
from sqlalchemy import desc, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem, CatalogImage, User, engine

# Perform CRUD Operation


class BaseDao(object):
    """
    Base Data Access
    """

    session = None

    def __init__(self):
        self.__init_session__()

    def __init_session__(self):
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()


class UserDao(BaseDao):
    """
        User Data Access Object
    """

    def get_all(self):
        return self.session. \
            query(User). \
            all()

    def find(self, user_id):
        return self.session. \
            query(User). \
            filter_by(id=id) . \
            one()

    def find_by_username(self, username):
        return self.session. \
            query(User). \
            filter_by(username=username) . \
            first()

    def save(self, user):
        self.session.add(user)
        self.session.commit()

    def save_all(self, users):
        for user in users:
            self.session.add(user)
        self.session.commit()

    def has_by_username(self, username):
        return self.session. \
            query(User). \
            filter_by(username=username). \
            count() > 0


class CategoryDao(BaseDao):
    """
    Category Data Access Object
    """

    def find_by_name(self, category_name):
        return self.session .\
            query(Category). \
            filter_by(name=category_name). \
            one()

    def get_all(self):
        return self.session. \
            query(Category). \
            all()

    def save(self, category):
        self.session.add(category)
        self.session.commit()

    def save_all(self, categories):
        for category in categories:
            self.session.add(category)
        self.session.commit()

    def delete(self, category_name):
        category = self.find_category_by_name(category_name)
        self.session.delete(category)
        self.session.commit()

    def count(self):
        return self.session. \
            query(func.count(Category.id)). \
            one()[0]


class CatalogItemDao(BaseDao):
    """
    CatalogItem Data Access Object
    """

    def get_lasteds(self):
        num_categories = CategoryDao().count()
        return self.session.query(CatalogItem). \
            order_by(desc(CatalogItem.id)). \
            limit(num_categories). \
            all()

    def get_by_category_name(self, category_name):
        return self.session. \
            query(CatalogItem). \
            join(CatalogItem.category). \
            filter(Category.name == category_name)

    def find(self, id):
        try:
            return self.session.query(CatalogItem). \
                filter_by(id=id). \
                one()
        except:
            print("Error find user by id (%s) " % id)

    def find_by_title(self, title):
        try:
            return self.session. \
                query(CatalogItem). \
                filter_by(title=title). \
                one()
        except:
            print("Erro find user by title (%s) " % title)

    def find_by_category_name_and_title(self, category_name, catalog_title):
        return self.session. \
            query(CatalogItem). \
            filter(Category.name == category_name, CatalogItem.title == catalog_title). \
            one()

    def has_item_by_title(self, title):
        return self.session. \
            query(CatalogItem). \
            filter_by(title=title). \
            count() > 0

    def insert(self, catalog_item):
        catalog_item.date = datetime.now()
        self.save(catalog_item)

    def save(self, catalog_item):
        self.session.add(catalog_item)
        return self.session.commit()

    def delete(self, catalog_item):
        self.session.delete(catalog_item)
        self.session.commit()


def create_sample_data():
    """
    Initializa database with sample data
    """

    user_dao = UserDao()

    user_den = user_dao.find_by_username("den@test.com")
    if (user_den):
        # Database has already been populated exit
        return

    print("")
    print("Creating sample data ...")
    print("Creating users ...")

    user_den = User(name="den", username="den@test.com")
    user_den.hash_password("123")

    user_maria = User(name="Maria", username="maria@test.com")
    user_maria.hash_password("123")

    user_dao.save_all([user_den, user_maria])

    print("Creating categories ...")

    category_names = ["Soccer", "Basketball", "Frisbie",
                      "Snowboarding", "Rock Climbing",
                      "Foosbal", "Skating", "Hockey"]

    categories = []

    for name in category_names:
        category = Category(name=name)
        categories.append(category)

    item_dao = CategoryDao()
    item_dao.save_all(categories)

    print("Data sample is created !!!")
    print("")
