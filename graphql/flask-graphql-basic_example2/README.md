## Documentation
https://docs.graphene-python.org/projects/sqlalchemy/en/latest/tutorial/

https://docs.graphene-python.org/projects/sqlalchemy/en/latest/tips/

https://docs.graphene-python.org/en/latest/types/mutations/

https://dev.to/mesadhan/python-flask-graphql-with-graphene-nla

http://www.leeladharan.com/sqlalchemy-query-with-or-and-like-common-filters

# Query builder (alternative)
https://pypika.readthedocs.io/en/latest/


## Running
python app.py runserver

127.0.0.1:5000/graphql

## Examples
{
  allEmployees {
    edges {
      node {
        id
        name
        department {
          name
        }
      }
    }
  }
}


{
  allDepartments {
    edges {
      node {
        id
        name
        city
      }
    }
  }
}


mutation {
  createDepartment(name: "marketing", city: "Cali") {
    department {
      name
      city
    }
    ok
  }
}


{
  findDepartment(name: "Engineering") {
    id,
    name,
    city
  }
}

{
  name(name: "Engineering") {
    id,
    name,
    city
  }
}

{
  city(city: "Santiago de Cali") {
    id,
    name,
    city
  }
}

{
 filterNameCity(name: "Engineering", city: "Santiago de Cali") { 
    id,
    name,
    city
 }
}

mutation {
	updateDepartment(name: "Engineering", city: "Santiago de Cali") {
    department {
      name
      city
    }
  }
}

mutation {
	deleteDepartment(name: "Engineering", city: "Cali") {
    department {
      name
      city
    }
  }
}


---------------------------

python3.7 seed.py

sqllite

sqlite3 database.sqlite3
.database
.tables
.schema department
.exit
