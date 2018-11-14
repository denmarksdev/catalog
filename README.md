# Catalog App

The application has a list of items within a variety of categories, as well as a user registration and authentication system.
The user can include, update and delete their own items.

# Requirments

1. Require **Python 2.7**
   - [Windows](https://www.python.org/downloads/windows/)
   - [Linux/Unix](https://www.python.org/downloads/source/)
   - [Mac](https://www.python.org/downloads/mac-osx/)
   - [Others](https://www.python.org/download/other/)
1. To use the third-party authentication system, you must have the following developer accounts:
   - [Google developer account](https://console.developers.google.com)
   - [Facebook developer account](https://developers.facebook.com/)

# Usage

1. Clone or download this repository
1. Install all dependencies with follow command `pip install -r dependencies.txt`
1. Download **JSON Google credentials APP** file and save file as **secrets_google.json** into root folder.
1. In the **secrets_facebook.json** replace **app_id** and **app_secret** your own credentials app.
1. Run app with foollow command-line `python application.json` 
 

# API JSON

Samples:

### http://localhost:8080/api/v1/catalog.json
Returns all categories and their respective Catalog Items.

```
{
  "Item": {
    "category_id": 1, 
    "description": "The ball used in the sport of association football. The name ...", 
    "id": 2, 
    "image": "http://localhost:8080/static/images/2.jpg", 
    "title": "Soccer Ball"
  }
}
```

### http://localhost:8080/api/v1/catalog.json/{item_title}

Returns all categories and their respective Catalog Items.
```
{
  "Category": [
    {
      "id": 1, 
      "item": [
        {
          "category_id": 1, 
          "description": "The ball used in the sport of association football ..." 
          "id": 2, 
          "image": "http://localhost:8080/static/images/2.jpg", 
          "title": "Soccer Ball"
        }
      ], 
      "name": "Soccer"
    }, 
    {
      "id": 4, 
      "item": [
        {
          "category_id": 4, 
          "description": "An object used for one of the greatest sports ever...", 
          "id": 1, 
          "image": "http://localhost:8080/static/images/1.png", 
          "title": "Snowboard"
        }
      ], 
      "name": "Snowboarding"
    }, 
    {
      "id": 5, 
      "item": [], 
      "name": "Rock Climbing"
    } 
  ]
}

```

# Screenshots
