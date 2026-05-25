- Crear un contenedor con la ultima version de mongodb
    - sudo docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password123 mongo:latest
- Instalar https://www.mongodb.com/products/tools/compass y conectarse a la base de datos.
- Create project with uv
    - uv init mongodb_test
    - uv venv
    - source .venv/bin/activate
    - uv add pymongo

