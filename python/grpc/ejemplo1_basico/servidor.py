import grpc
from concurrent import futures

# Importamos los archivos autogenerados a partir de hola.proto
import hola_pb2
import hola_pb2_grpc

# Se crea una clase que hereda de la clase base generada por gRPC
class ServicioSaludo(hola_pb2_grpc.ServicioSaludoServicer):
    
    # Se implementa el metodo "Saludar" definido en el archivo .proto
    def Saludar(self, request, context):
        print(f"[SERVIDOR] Saludar a: {request.nombre}")
        
        # Logica del servidor: preparamos un saludo personalizado
        mensaje_saludo = f"Hola {request.nombre}! Bienvenido a gRPC."
        
        # Se instancia la clase de respuesta del compilado y se le envian los datos
        return hola_pb2.RespuestaSaludo(mensaje=mensaje_saludo)

def iniciar_servidor():
    # Se crea un servidor local gRPC capaz de atender hasta 10 clientes simultaneos (hilos)
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Se añade la clase recien definida a las rutas del servidor de la libreria
    hola_pb2_grpc.add_ServicioSaludoServicer_to_server(ServicioSaludo(), servidor)
    
    # Se escucha de forma insegura en el puerto 50051 (puerto comunmente usado por gRPC)
    servidor.add_insecure_port('[::]:50051')
    servidor.start()
    print("Servidor gRPC Básico escuchando localmente en el puerto 50051...")
    
    # Se mantiene el hilo de logica principal vivo para que no se apague
    servidor.wait_for_termination()

if __name__ == '__main__':
    iniciar_servidor()
