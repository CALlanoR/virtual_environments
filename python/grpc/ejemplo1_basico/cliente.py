import grpc

# Importamos los archivos generados desde el protobuf
import hola_pb2
import hola_pb2_grpc

def ejecutar_peticion():
    print("Iniciando comunicacion gRPC...")
    
    # Se conecta al puerto que el servidor definió usando un canal sin encriptacion TLS
    with grpc.insecure_channel('localhost:50051') as canal:
        
        # Se crea el cliente que llamara los metodos ("stub" es esqueleto/puente al servidor)
        stub = hola_pb2_grpc.ServicioSaludoStub(canal)
        
        # Se prepara el mensaje de peticion como objeto Python, definiendo sus propiedades
        print("Preparando peticion...")
        peticion = hola_pb2.PeticionSaludo(nombre="Wachu")
        
        # Se realiza la llamada remota como si unicamente fuera una funcion local
        respuesta = stub.Saludar(peticion)
        
    # Acabada la peticion (el canal with grpc. se cerrará aquí autómaticamente)
    print(f"Respuesta exitosa del servidor:\n > {respuesta.mensaje}")

if __name__ == '__main__':
    ejecutar_peticion()
