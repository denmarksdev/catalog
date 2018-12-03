# Catalog Models

from app import db
from app.mod_auth.models import User
from config import PUBLIC_URL


class Category(db.Model):
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


class CatalogImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    suffix = db.Column(db.String(5), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

    def get_name(self):
        return '%s.%s' % (self.id, self.suffix,)

    def get_url(self, base_url):
        """
        Define access a url image, base URL can change.
        base_url refers to a public address
        """
        return ("%s/static/images/%s"
                % (base_url, self.get_name(),))


class CatalogItem(db.Model):
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
    image = db.relationship(CatalogImage,
                            cascade="all, delete-orphan",
                            single_parent=True)

    @property
    def serialize(self, base_url=PUBLIC_URL):
        # Returns object in easily serializeable
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': self.image.get_url(base_url),
            'category_id': self.category_id
        }
