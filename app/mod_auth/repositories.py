from models import User


class RepositoryBase:
    def __init__(self, db_session):
        self.session = db_session

    def commit(self):
        self.session.commit()


class UserRepository(RepositoryBase):
    """
    User object-oriented view of the persistence layer
    """

    def __init__(self, session_db):
        RepositoryBase.__init__(self, session_db)

    def all(self):
        return User.query .\
            all()

    def find(self, user_id):
        return User.query. \
            filter_by(id=user_id) . \
            one_or_none()

    def find_by_username(self, username):
        return User.query. \
            filter_by(username=username) . \
            first()

    def add(self, user):
        self.session.add(user)

    def add_all(self, users):
        for user in users:
            self.session.add(user)

    def has_by_username(self, username):
        return User.query.\
            filter_by(username=username). \
            count() > 0
