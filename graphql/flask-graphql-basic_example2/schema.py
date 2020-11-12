import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, Department as DepartmentModel, Employee as EmployeeModel

class Department(SQLAlchemyObjectType):
    class Meta:
        model = DepartmentModel
        interfaces = (relay.Node, )

class Employee(SQLAlchemyObjectType):
    class Meta:
        model = EmployeeModel
        interfaces = (relay.Node, )

# Used to Create New Department
class CreateDepartment(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        city = graphene.String()

    ok = graphene.Boolean()
    department = graphene.Field(lambda: Department)

    def mutate(self, context, **kwargs):
        name=kwargs.get('name')
        city = kwargs.get('city')
        department = DepartmentModel(name=name, city=city)
        db_session.add(department)
        db_session.commit()
        ok = True
        return CreateDepartment(department=department, ok=ok)

# Used to Change Department with Name
class UpdateDepartment(graphene.Mutation):

    class Arguments:
        name=graphene.String()
        city=graphene.String()

    ok = graphene.Boolean()
    department = graphene.Field(Department)

    def mutate(self, context, **kwargs):
        query = Department.get_query(context)
        name=kwargs.get('name')
        city = kwargs.get('city')

        department = query.filter(DepartmentModel.name == name).first()
        department.city = city
        db_session.commit()
        ok = True
        return UpdateDepartment(department=department, ok = ok)

class DeleteDepartment(graphene.Mutation):
    class Arguments:
        name=graphene.String()
        city=graphene.String()

    ok = graphene.Boolean()
    department=graphene.Field(Department)     

    def mutate(self, context, **kwargs):
        query=Department.get_query(context)
        name=kwargs.get('name')
        city=kwargs.get('city')

        department=query.filter(DepartmentModel.name==name, DepartmentModel.city==city).delete()
        db_session.commit()
        ok=True        

        return DeleteDepartment(department=department, ok = ok)

class MyMutations(graphene.ObjectType):
    create_department = CreateDepartment.Field()
    update_department = UpdateDepartment.Field()
    delete_department = DeleteDepartment.Field()

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    # Allows sorting over multiple columns, by default over the primary key
    all_employees = SQLAlchemyConnectionField(Employee.connection)

    # Disable sorting over this field
    all_departments = SQLAlchemyConnectionField(Department.connection, sort=None)

    # Find department by name
    find_department = graphene.Field(lambda: Department, name=graphene.String())

    def resolve_find_department(self, context, **kwargs):
        return Department.get_query(context).filter_by(**kwargs).first()

    # Find department by city
    find_department = graphene.Field(lambda: Department, name=graphene.String())

    def resolve_find_department(self, context, **kwargs):
        return Department.get_query(context).filter_by(**kwargs).first()

schema = graphene.Schema(query=Query,
                         mutation=MyMutations)



    # def resolve_user(self, info, id):
    #     return [user for user in users if user.id == int(id)]