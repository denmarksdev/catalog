from app.mod_auth.repositories import UserRepository
from app.mod_catalog.repositories import CategoryRepository, \
    CatalogItemRepository


class RepositoryBase:
    def __init__(self, db_session):
        self.session = db_session

    def commit(self):
        self.session.commit()


class CatalogUnitOfWorkManager():
    """The Unit of work manager returns a new unit of work. 
       Our UOW is backed by a sql alchemy session whose 
       lifetime can be scoped to a web request, or a 
       long-lived background job."""

    def __init__(self, session_maker):
        self.session_maker = session_maker

    def start(self):
        return CatalogUnitOfWork(self.session_maker)


class CatalogUnitOfWork():
    """The unit of work captures the idea of a set of things that
       need to happen together. 
       Usually, in a relational database, 
       one unit of work == one database transaction."""

    def __init__(self, sessionfactory):
        self.session = sessionfactory

    def __enter__(self):
        self.session = self.sessionfactory()
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    @property
    def users(self):
        return UserRepository(self.session)

    @property
    def categories(self):
        return CategoryRepository(self.session)

    @property
    def catalog_items(self):
        return CatalogItemRepository(self.session)
