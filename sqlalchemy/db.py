from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///productos.sqlite')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Pool de conexiones
# SQLAlchemy utiliza el patrón Pool de objetos para manejar las conexiones a la base de datos. 
# Esto quiere decir que cuando se usa una conexión a la base de datos, esta ya está creada previamente 
# y es reutilizada por el programa. La principal ventaja de este patrón es que mejora el rendimiento de 
# la aplicación, dado que abrir y gestionar una conexión de base de datos es una operación costosa y que 
# consume muchos recursos.

# Al crear un engine con la función create_engine(), se genera un pool QueuePool que viene configurado 
# como un pool de 5 conexiones como máximo. Esto se puede modificar en la configuración de SQLAlchemy.
