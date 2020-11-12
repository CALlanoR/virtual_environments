
https://docs.graphene-python.org/projects/sqlalchemy/en/latest/tutorial/

https://docs.graphene-python.org/projects/sqlalchemy/en/latest/tips/

https://docs.graphene-python.org/en/latest/types/mutations/

https://dev.to/mesadhan/python-flask-graphql-with-graphene-nla

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
  createDepartment(name: "marketing", city: "Medellin") {
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
