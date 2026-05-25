import grpc

import universidad_pb2
import universidad_pb2_grpc

def probar_universidad():
    # Usamos channel (canal) de comunicacion inseguro (sin TLS) para aprender localmente
    with grpc.insecure_channel('localhost:50051') as canal:
        stub = universidad_pb2_grpc.SistemaUniversitarioStub(canal)
        
        # ------------- TEST 1: Buscar alguien que SI existe
        print("\n=== TEST 1: OBTENER ESTUDIANTE EXISTENTE (ID=101) ===")
        # Empacamos el mensaje int32 especifico
        peticion_obtener = universidad_pb2.IdEstudiante(id_estudiante=101)
        try:
            # ¡Hacemos el envio RPC!
            estudiante = stub.ObtenerEstudiante(peticion_obtener)
            print(">>> ESTUDIANTE ENCONTRADO EN LA BD <<<<")
            print(f"- Nombre: {estudiante.nombre}")
            print(f"- Carrera: {estudiante.carrera}")
            print(f"- Semestre: {estudiante.semestre}°")
        except grpc.RpcError as e:
            print(f"Error gRPC: {e.details()}")

        # ------------- TEST 2: Buscar alguien que NO existe
        print("\n=== TEST 2: OBTENER ESTUDIANTE NO EXISTENTE (ID=999) ===")
        peticion_obtener_fallo = universidad_pb2.IdEstudiante(id_estudiante=999)
        try:
            fallo = stub.ObtenerEstudiante(peticion_obtener_fallo)
        except grpc.RpcError as e:
            # Aquí la red neuronal de cliente capta exactamente el "NOT_FOUND" que lanzamos
            print(f"Se capturo Excepción del Servidor intencionalmente: {e.details()}")

        # ------------- TEST 3: Llamar Metodo y Mensajes completamente distintos
        print("\n=== TEST 3: REGISTRAR UN NUEVO ESTUDIANTE ===")
        # Cremos un mensaje tipo NuevoEstudiante (definido en proto)
        peticion_registro = universidad_pb2.NuevoEstudiante(
            nombre="Laura Jimenez",
            carrera="Derecho",
            semestre=1
        )
        
        # Desencadenamos el segundo metodo por la red local
        respuesta_registro = stub.RegistrarEstudiante(peticion_registro)
        if respuesta_registro.exito:
            print(f"Resultado del tramite: {respuesta_registro.mensaje}")
            print(f"Credencial asignada del alumno: #{respuesta_registro.id_asignado}")
        else:
            print("Oh no, fallo el registro de estudiante.")

if __name__ == '__main__':
    probar_universidad()
