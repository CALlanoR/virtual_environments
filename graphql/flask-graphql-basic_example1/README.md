## Documentation

https://medium.com/@marvinkome/creating-a-graphql-server-with-flask-ae767c7e2525

https://graphql.org/
GraphQL is a query language for APIs and a runtime for fulfilling those queries with your existing data. GraphQL provides a complete and understandable description of the data in your API, gives clients the power to ask for exactly what they need and nothing more, makes it easier to evolve APIs over time, and enables powerful developer tools.

we will be using the Graphene-Python package. Graphene is an open-source library that allows developers to build simple yet extendable APIs with GraphQL in Python.

python app.py runserver

127.0.0.1:5000/graphql

{
  allPosts{
    edges{
      node{
        title
        body
        author{
          username
        }
      }
    }
  }
}



Add some data:
$ python
>>> from app import db, User, Post
>>> db.create_all()
>>> john = User(username='johndoe')
>>> post = Post()
>>> post.title = "Hello World"
>>> post.body = "This is the first post"
>>> post.author = john
>>> db.session.add(post)
>>> db.session.add(john)
>>> db.session.commit()
>>> User.query.all()
[<User 'johndoe'>]
>>> Post.query.all()
[<Post 'Hello World'>