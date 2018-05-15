Building a Typical Web API
==========================
Our first draft API will be a read-only version and will not support creating or updating items in the catalog as real-world applications do. Instead, we will concentrate on the API definition itself.

Our first draft API will be a read-only version and will not support creating or updating items in the catalog as real-world applications do. Instead, we will concentrate on the API definition itself.


1. Specifying the API
=====================
----------------------------------------------------------------------------------------------------------------------------------
| Method | URI                               | Description                                                                       |
----------------------------------------------------------------------------------------------------------------------------------
| GET    | /category                         | Retrieves all available categories in the catalog.                                |
| GET    | /category/{category-id}/          | Retrieves all the items available under a specific category.                      |
| GET    | /category/{category-id}/{item-id} | Retrieves an item by its ID under a specific category.                            |
| POST   | /category                         | Creates a new category; if it exists, it will update it.                          |
| POST   | /category/{category-id}/          | Creates a new item in a specified category. If the item exists, it will update it.|
| PUT    | /category/{category-id}           | Updates a category.                                                               |  
| PUT    | /category/{category-id}/{item-id} | Updates an item in a specified category.                                          |
| DELETE | /category/{category-id}           | Deletes an existing category.                                                     |
| DELETE | /category/{category-id}/{item-id} | Deletes an item in a specified category.                                          |
----------------------------------------------------------------------------------------------------------------------------------

2. To choose an appropriate format
==================================
JSON objects are natively supported by JavaScript. They are easy to extend during the evolution of an application and are consumable by almost any platform available. Examples:

{ 
    "itemId": "item-identifier-1", 
    "itemName": "Sports Watch", 
    "category": "Watches", 
    "categoryId": 1,
    "price": 150, 
    "currency": "EUR"
} 

{
    "categoryName" : "Watches",
    "categoryId" : "1",
    "itemsCount" : 100,
    "items" : [{
            "itemId" : "item-identifier-1",
            "itemName":"Sports Watch",
            "price": 150,
            "currency" : "EUR"    
     }]
}


3. mkdir workdir
4. cd workdir
5. npm install -g express-generator
6. express catalog_api
7. cd catalog_api
8. As you can see, Express has done some background work for us and has created a starting point for our application: app.js. It has also created the package.json file for us. Let's take a look at each of these files:
    8.1 cat package.json
    8.2 cat app.js
        8.2.1 You will have to install all the modules used in app.js in order to start the generated application successfully
              8.2.1.1 npm install body-parser express cookie-parser debug jade pug morgan serve-favicon http http-errors
    8.3 The Express generator also created a starting script for the application. It is under the  bin/www
        8.3.1 vi bin/www
        8.3.2 in bin/www Change the port 3000 for 8180
        8.3.3 node bin/www
9. http://127.0.0.1:8180/
10. The generator created a dummy routes/users.js; it exposes a route linked to a dummy module available at the /users location. Requesting it will result in calling the list function of the user's route, which outputs a static response: respond with a resource.
    10.1 http://127.0.0.1:8180/users
    10.2 vi routes/users.js

11. Create our catalag route

vi routes/catalog.js

-----------------------------------------------------------------------------
| HTTP method |  Route                       | Catalog's module function    |
-----------------------------------------------------------------------------
| GET         | /catalog                     | findCategories()             |
| GET         | /catalog/:categoryId         | findItems(categoryId)        |
| GET         | /catalog/:categoryId/:itemId | findItem(categoryId, itemId) |
-----------------------------------------------------------------------------

put this:

var express = require('express');
var catalog = require('../modules/catalog.js')

var router = express.Router();

router.get('/', function(request, response, next) {
  var categories = catalog.findCategoryies();
  response.json(categories);
});

router.get('/:categoryId', function(request, response, next) {
  var categories = catalog.findItems(request.params.categoryId);
  if (categories === undefined) {
    response.writeHead(404, {'Content-Type' : 'text/plain'});
    response.end('Not found');
  } else {
    response.json(categories);
  }
});

router.get('/:categoryId/:itemId', function(request, response, next) {
  var item = catalog.findItem(request.params.categoryId, request.params.itemId);
  if (item === undefined) {
    response.writeHead(404, {'Content-Type' : 'text/plain'});
    response.end('Not found');
  } else {
  response.json(item);
  }
});
module.exports = router;


12. Create directory modules
13. cd modules
14. vi catalog.js

Put this:

var fs = require('fs');

function readCatalogSync() {
   var file = './data/catalog.json';
   if (fs.existsSync(file)) {
     var content = fs.readFileSync(file);
     var catalog = JSON.parse(content);
     return catalog;
   }
   return undefined;
 }

exports.findItems = function(categoryId) {
  console.log('Returning all items for categoryId: ' + categoryId);
  var catalog = readCatalogSync();
  if (catalog) {
    var items = [];
    for (var index in catalog.catalog) {
        console.log('-------' + catalog.catalog[index])
        if (catalog.catalog[index].categoryId === categoryId) {
          var category = catalog.catalog[index];
          for (var itemIndex in category.items) {
            items.push(category.items[itemIndex]);
          }
        }
    }
    return items;
  }
  return undefined;
}

exports.findItem = function(categoryId, itemId) {
  console.log('Looking for item with id' + itemId);
  var catalog = readCatalogSync();
  if (catalog) {
    for (var index in catalog.catalog) {
        if (catalog.catalog[index].categoryId === categoryId) {
          var category = catalog.catalog[index];
          for (var itemIndex in category.items) {
            if (category.items[itemIndex].itemId === itemId) {
              return category.items[itemIndex];
            }
          }
        }
    }
  }
  return undefined;
}

exports.findCategoryies = function() {
  console.log('Returning all categories');
  var catalog = readCatalogSync();
  if (catalog) {
    var categories = [];
    for (var index in catalog.catalog) {
        var category = {};
        category["categoryId"] = catalog.catalog[index].categoryId;
        category["categoryName"] = catalog.catalog[index].categoryName;

        categories.push(category);
    }
    return categories;
  }
  return [];
}

15. delete app.js and vi app.js

Put this:

var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');

var routes = require('./routes/index');
var catalog = require('./routes/catalog')
var app = express();

//uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', routes);
app.use('/catalog', catalog);


// catch 404 and forward to error handler
app.use(function(req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

//development error handler will print stacktrace
if (app.get('env') === 'development') {
  app.use(function(err, req, res, next) {
    res.status(err.status || 500);
    res.render('error', {
      message: err.message,
      error: err
    });
  });
}

// production error handler no stacktraces leaked to user
app.use(function(err, req, res, next) {
  res.status(err.status || 500);
  res.render('error', {
    message: err.message,
    error: {}
  });
});

module.exports = app;


16. create directory data
17. vi data/catalog.json

Put this:

{"catalog" : [
    { 
      "categoryName" : "Watches",
      "categoryId" : "1",
      "itemsCount" : 2,
      "items" : [
        {
            "itemId" : "item-identifier-1",
            "itemName":"Sports Watch",
            "price": 150,
            "currency" : "EUR"
        },
        {
             "itemId" : "item-identifier-2",
             "itemName":"Waterproof Sports Watch",
             "price": 180,
             "currency" : "EUR"
        }]
    }]
}

18. http://127.0.0.1:8180/catalog/1
19. http://127.0.0.1:8180/catalog/1/item-identifier-1
20. http://127.0.0.1:8180/catalog/


So far, the catalog service supports only the JSON format, and thus works only with the media type application/json. Let's assume our service has to offer data in different formats, for example, both JSON and XML. Then, the consumer needs to explicitly define the data format they need. 

 let's assume we have implemented a function within our catalog module, named findCategoriesXml, that provides the group data in XML format:

app.get('/catalog', function(request, response) { 
    response.format( { 
      'text/xml' : function() { 
         response.send(catalog.findCategoriesXml()); 
      }, 
      'application/json' : function() { 
         response.json(catalog.findCategoriesJson()); 
      }, 
      'default' : function() {. 
         response.status(406).send('Not Acceptable'); 
      }    
    }); 
}); 