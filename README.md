# Catalog App

The application has a list of items within a variety of categories, as well as a user registration and authentication system.
The user can include, update and delete their own items.

# Requirements

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
1. Install all dependencies with the following command `pip install -r dependencies.txt`
1. Download **Google JSON** file and save the file as **secrets_google.json** into the root folder.
   - ![](https://github.com/denmarksdev/catalog/blob/master/google_console.JPG?raw=true "Reporter tool")
1. In the **secrets_facebook.json** replace **app_id** and **app_secret** your own credentials app.
   - ![](https://github.com/denmarksdev/catalog/blob/master/facebook_config.jpg?raw=true "Reporter tool")
1. Run app with foollow command `python application.json` 
 

# API JSON

Samples:

### http://localhost:8080/api/v1/catalog.json/{item_title}
Return Catalog Item by Title
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
### http://localhost:8080/api/v1/catalog.json
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
## Catalog

![](https://github.com/denmarksdev/catalog/blob/master/catalog.JPG?raw=true "Catalog")

## Catalog Item Details

![](https://github.com/denmarksdev/catalog/blob/master/catalog-item-details.JPG?raw=true "Catalog Item Details")

## Catalog in Mobile

![](https://github.com/denmarksdev/catalog/blob/master/catalog-mobile.JPG?raw=true "Catalog in mobile")
