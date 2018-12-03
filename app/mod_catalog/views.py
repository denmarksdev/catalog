# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db


class Category(Base):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    items = db.relationship('CatalogItem')

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

    id = db.Column(db.Integer, primary_key=True)
    suffix = db.Column(db.String(5), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

    def get_name(self):
        return '%s.%s' % (self.id, self.suffix,)


class CatalogItem(Base):
    __tablename__ = 'catalog_item'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(800), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    User = db.relationship(User)

    category_id = db.Column(db.Integer(), db.ForeignKey('category.id'))
    category = db.relationship(Category)

    catalog_image_id = db.Column(
        db.Integer(), db.ForeignKey('catalog_image.id'))
    image = db.relationship(
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
