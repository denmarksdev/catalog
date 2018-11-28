from sqlalchemy import (Column, ForeignKey,
                        Integer, String, DateTime,
                        LargeBinary, UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
# PASSWORD HASH
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    picture = Column(String(250))
    username = Column(String(100), nullable=False)
    password_hash = Column(String)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    items = relationship('CatalogItem')

    @property
    def serialize_with_catalog_items(self):
        # Returns object in easily serializeable
        return {
            'id': self.id,
            'name': self.name,
            'item': [i.serialize for i in self.items]
        }


class CatalogImage(Base):
    __tablename__ = 'catalog_image'

    id = Column(Integer, primary_key=True)
    suffix = Column(String(3), nullable=False)
    data = Column(LargeBinary, nullable=False)

    def get_name(self):
        return '%s.%s' % (self.id, self.suffix,)


class CatalogItem(Base):
    __tablename__ = 'catalog_item'

    id = Column(Integer, primary_key=True)
    title = Column(String(20), nullable=False)
    description = Column(String(800), nullable=False)
    date = Column(DateTime, nullable=False)

    user_id = Column(Integer(), ForeignKey('user.id'))
    User = relationship(User)

    category_id = Column(Integer(), ForeignKey('category.id'))
    category = relationship(Category)

    catalog_image_id = Column(Integer(), ForeignKey('catalog_image.id'))
    image = relationship(
        CatalogImage, cascade="all, delete-orphan", single_parent=True)

    @property
    def serialize(self):
        # Returns object in easily serializeable
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': ("http://localhost:8080/static/images/%s"
                      % self.image.get_name()),
            'category_id': self.category_id
        }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
