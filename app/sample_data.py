from app import db
from datetime import datetime
from app.mod_auth.models import User
from app.mod_catalog.models import Category, CatalogItem, CatalogImage
from app.unit_of_work import CatalogUnitOfWorkManager
from config import IMAGE_DIR


def create(path):
    """
    Initializa database with sample data
    """

    print path

    db.create_all()

    # Manages persistence of data as a single transaction
    uow = CatalogUnitOfWorkManager(db.session).start()

    # Verify the database allready populate

    user_den = uow.users.find_by_username("den@test.com")
    if (user_den):
        return

    print("")
    print("Creating sample data ...")

    # Create user
    print("Creating users ...")

    user_den = User(name="den", username="den@test.com")
    user_den.hash_password("123")

    user_maria = User(name="Maria", username="maria@test.com")
    user_maria.hash_password("123")

    uow.users.add_all([user_den, user_maria])

    # Create categories
    print("Creating categories ...")

    category_names = ["Soccer", "Basketball", "Frisbie",
                      "Snowboarding", "Rock Climbing",
                      "Foosbal", "Skating", "Hockey"]

    categories = []

    for name in category_names:
        category = Category()
        category.name = name
        categories.append(category)

    uow.categories.add_all(categories)

    # Create CatalogItems
    print("Creating Snowboard item")
    category = uow.categories.find_by_name("Snowboarding")
    item = CatalogItem(title="Snowboard",
                       date=datetime.now(),
                       user_id=user_den.id,
                       category_id=category.id)
    item.description = """
    An object used for one of the greatest sports ever...SNOWBOARDING.
    Whether you're carving down a steep mountainside,     ripping up
    the park with insane mad shit, just cruising or a beginner...Once
    you go, Board, you never go back.
    """
    # Create image sample
    file = open(IMAGE_DIR + "/snowboard.jpg")
    image = CatalogImage()
    image.data = file.read()
    image.suffix = "png"
    item.image = image
    uow.catalog_items.add_with_date(item)

    # Create Image file from database
    item = uow.catalog_items.find_by_title("Snowboard")
    file = open(IMAGE_DIR + "/" + item.image.get_name(), 'w+')
    file.write(item.image.data)

    print("Creating Soccer Ball")
    category = uow.categories.find_by_name("Soccer")
    item = CatalogItem(title="Soccer Ball",
                       date=datetime.now(),
                       user_id=user_maria.id,
                       category_id=category.id)
    item.description = """
    is the ball used in the sport of association football. The name of the ball
    varies according to whether the sport is called "football", "soccer", or
    "association football". The ball's spherical shape, as well as its size,
    weight, and material composition, are specified by Law 2 of the Laws of
    the Game maintained by the International Football Association Board.
    Additional, more stringent, standards are specified by FIFA and
    subordinate governing bodies for the balls used in the
    competitions they sanction.
    """

    # Create image sample
    file = open(IMAGE_DIR + "/soccer-ball.jpg")
    image = CatalogImage()
    image.data = file.read()
    image.suffix = "jpg"
    item.image = image

    uow.catalog_items.add_with_date(item)

    # Create Image file from database
    item = uow.catalog_items.find_by_title("Soccer Ball")

    file = open(IMAGE_DIR + "/" + item.image.get_name(), 'w+')
    file.write(item.image.data)

    # Confirm transaction on database
    uow.commit()

    print("Sample data is created :)")

    print("")
