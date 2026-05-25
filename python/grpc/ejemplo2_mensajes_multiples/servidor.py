import grpc
from concurrent import futures

import universidad_pb2
import universidad_pb2_grpc

# Nuestra "Base de datos" en memoria
# Es un diccionario de pyhton simple con llave Id, valor Diccionario de info
ESTUDIANTES_DB = {
    101: {"nombre": "Ana Perez", "carrera": "Ingeniería de Sistemas", "semestre": 5},
    102: {"nombre": "Carlos Rojas", "carrera": "Medicina", "semestre": 3}
}

# Auto-incrementador basico para alumnos nuevos
ID_ACTUAL = 103

class SistemaUniversitario(universidad_pb2_grpc.SistemaUniversitarioServicer):
    
    # Metodo 1: Buscar estudiante
    def ObtenerEstudiante(self, request, context):
        id_buscado = request.id_estudiante
        print(f"[SERVIDOR] Un cliente solicita la informacion del ID: {id_buscado}")
        
        if id_buscado in ESTUDIANTES_DB:
            datos = ESTUDIANTES_DB[id_buscado]
            # Devolvemos un mensaje de Protocol Buffer de tipo InfoEstudiante con los atributos mapados
            return universidad_pb2.InfoEstudiante(
                id_estudiante=id_buscado,
                nombre=datos["nombre"],
                carrera=datos["carrera"],
                semestre=datos["semestre"]
            )
        else:
            # Si no existe, usamos los errores nativos integrados de gRPC para rechazar
            # la petición con el tag especifico "NOT_FOUND".
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Error HTTP/2: El estudiante con id {id_buscado} no existe en la BD.")
            
            # Devolvemos objeto vacio porque gRPC de igual forma mandará el error (exception) al channel
            return universidad_pb2.InfoEstudiante()

    # Metodo 2: Registrar un nuevo estudiante
    def RegistrarEstudiante(self, request, context):
        global ID_ACTUAL
        print(f"[SERVIDOR] Se solicita inscripcion para la carrera de {request.carrera} a nombre de {request.nombre}")
        
        nuevo_id = ID_ACTUAL
        ID_ACTUAL += 1
        
        # Guardamos en la "Base de Datos" temporal
        ESTUDIANTES_DB[nuevo_id] = {
            "nombre": request.nombre,
            "carrera": request.carrera,
            "semestre": request.semestre
        }
        
        # Respondemos con el boolean positivo y confirmamos la transaccion al cliente
        return universidad_pb2.RespuestaRegistro(
            exito=True,
            mensaje="Alumno incorporado en la institucion exitosamente. ¡A estudiar!",
            id_asignado=nuevo_id
        )

def activar_universidad():
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    universidad_pb2_grpc.add_SistemaUniversitarioServicer_to_server(SistemaUniversitario(), servidor)
    servidor.add_insecure_port('[::]:50051')
    servidor.start()
    print("Servidor de Sistema Universitario Corriendo (Puerto: 50051)...")
    try:
        servidor.wait_for_termination()
    except KeyboardInterrupt:
        print("Servidor detenido por teclado.")

if __name__ == '__main__':
    activar_universidad()
