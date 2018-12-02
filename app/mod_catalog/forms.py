# Import Form
from flask_wtf import FlaskForm

# Import Form elements such as TextField, PasswordField
from wtforms import TextField, SelectField, HiddenField

# Make input image some validations
from flask_uploads import UploadSet, IMAGES
from flask_wtf.file import FileField, FileAllowed

# Import Form validators
from wtforms.validators import Required

images = UploadSet('images', IMAGES)


class ItemForm(FlaskForm):
    """
    Define the CatalogItem form (WTForms)
    """
    title = TextField('Tilte', [
        Required(message='Forget the title?')])
    description = TextField('Description', [
        Required(message='Forger the description?')])
    image = FileField('image', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
    categories = SelectField('Categories', coerce=int)

    def setCategories(self, categories):
        """
        Set categories from external source
        """
        self.categories.choices = [
            (c.id, c.name) for c in categories
        ]


class ItemDeleteForm(FlaskForm):
    """
    User for only delete Catalog item, does not need inputs.
    """
