import pymysql
from app import app
from db_config import mysql
from flask import jsonify
from flask import flash, request
from werkzeug import generate_password_hash, check_password_hash

@app.route('/rol', methods=['POST'])
def add_rol():
    try:
        _json = request.json
        _name = _json['name']
        # validate the received values
        if _name and request.method == 'POST':
            sql = "INSERT INTO roles(name) VALUES(%s)"
            data = (_name,)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            resp = jsonify({'id': cursor.lastrowid})
            resp.status_code = 200
            return resp
        else:
            return not_found()
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()
        
@app.route('/rol', methods=['GET'])
def get_all_roles():
    try:
        page = request.args.get('page', default = 1, type = int)
        name = request.args.get('name', default = None, type = str)
        app.logger.info("page: " + str(page))
        
        pagesize = 2
        startat = page*pagesize

        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if name:
            cursor.execute("SELECT id, name FROM roles WHERE name LIKE %s LIMIT %s, %s", (name,startat, pagesize))
        else:
            cursor.execute("SELECT id, name FROM roles LIMIT %s, %s", (startat, pagesize))

        rows = cursor.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()

@app.route('/rol/<int:id>', methods=['GET'])
def get_rol_by_id(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, name FROM roles WHERE id=%s", id)
        row = cursor.fetchone()
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()

@app.route('/rol/<int:id>', methods=['PUT'])
def update_rol(id):
    try:
        _json = request.json
        _name = _json['name']		
        # validate the received values
        if _name and id and request.method == 'PUT':
            # save edits
            sql = "UPDATE roles SET name=%s WHERE id=%s"
            data = (_name, id,)
            conn = mysql.connect()
            cursor = conn.cursor()
            rows_affected = cursor.execute(sql, data)
            app.logger.info("PUT update_rol, rows_affected: " + str(rows_affected))
            if rows_affected == 0:
                resp = jsonify({'message': 'Rol was not updated!'})
                resp.status_code = 200
            else:
                resp = jsonify({'message': 'Rol updated successfully!'})
                resp.status_code = 200
            conn.commit()
            return resp
        else:
            return not_found()
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()
        
@app.route('/rol/<int:id>', methods=['DELETE'])
def delete_rol(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        rows_affected = cursor.execute("DELETE FROM roles WHERE id=%s", (id,))
        conn.commit()
        if rows_affected == 0:
            resp = jsonify({'message': 'Rol was not deleted!'})
            resp.status_code = 200
        else:
            resp = jsonify({'message': 'Rol deleted successfully!'})
            resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')