# Guía Completa de gRPC con Python para Estudiantes

¡Hola a todos! En esta guía aprenderemos paso a paso qué es gRPC, cómo funciona, y cómo podemos construir aplicaciones de cliente/servidor eficientes usando Python.

## ¿Qué es gRPC?

gRPC (gRPC Remote Procedure Call) es un marco (framework) moderno de código abierto desarrollado inicialmente por Google. Permite que aplicaciones distribuidas se comuniquen entre sí de una manera rápida y eficiente como si fueran llamadas a procedimientos o métodos locales.

Imagina que tienes una aplicación en Python (Cliente) que necesita enviar datos y pedirle a otra aplicación en Python (Servidor) que haga una operación. Tradicionalmente usarías una API REST (con JSON y peticiones HTTP). Con gRPC, usas código autogenerado que permite comunicarse mediante Protocol Buffers y HTTP/2, lo cual es mucho más veloz y consumiendo menos ancho de banda.

## ¿Qué son los Protocol Buffers?

Protocol Buffers (a menudo abreviados como Protobuf) es el formato de mensaje estándar que usa gRPC. Es un mecanismo neutral, funciona con diferentes lenguajes y plataformas. Su meta es definir la estructura de tus datos, permitiendo serializarlos para enviarlos a través de la red de manera muy pequeña, más rápida y más simple que JSON o XML.

Los definimos creando archivos con extensión `.proto`.

## Preparando nuestro Entorno

Antes de comenzar a explorar los ejemplos, necesitamos instalar las librerías necesarias. Ejecuta este comando en tu terminal:

```bash
pip install grpcio grpcio-tools
```

* `grpcio`: La librería oficial de gRPC para Python.
* `grpcio-tools`: Herramientas esenciales para leer nuestros archivos `.proto` y compilar ("traducir") esas estructuras en clases y métodos que Python entienda sin problemas.

---

## Ejemplo 1: Comunicación Básica (Un mensajito y una respuesta)

Si navegas al directorio llamado `ejemplo1_basico`, encontrarás el clásico "Hola Mundo" pero con gRPC.

### 1. El archivo `.proto` (`ejemplo1_basico/hola.proto`)

Acá definimos un Servicio (`ServicioSaludo`) y los Mensajes que intercambia (`PeticionSaludo` y `RespuestaSaludo`). Cada variable de los mensajes debe llevar un identificador de campo único (ej. `= 1;`).

### 2. Generando el código Python

Para que Python entienda el archivo `.proto`, se debe compilar. **Entrar a la carpeta** `ejemplo1_basico` **en la terminal** y ejecutar:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. hola.proto
```
Si mira los archivos de la carpeta, verás archivos nuevos:
- `hola_pb2.py`: Contiene las clases de los mensajes de datos (PeticionSaludo, RespuestaSaludo).
- `hola_pb2_grpc.py`: Contiene las lógicas y plantillas de conexión de gRPC del cliente y del servidor.

### 3. El Servidor y el Cliente

* En **`servidor.py`**: se implementa la clase que hereda de los archivos autogenerados. Ahí se dice *qué debe pasar* lógicamente cuando alguien invoca la función `Saludar`.
* En **`cliente.py`**: se crea un "stub" (canal abierto al servidor) por donde se llama a `Saludar` pasándole una Petición tal como si llamaramos a una función local de nuestro propio código.

**Probar:**
1. Abrir una terminal y ejecutar: `python servidor.py` (Dejando la consola abierta).
2. Abrir una **segunda** terminal (en la misma carpeta) y ejecutar: `python cliente.py`.

---

## Ejemplo 2: Múltiples Mensajes y Tipos 

En la carpeta `ejemplo2_mensajes_multiples` sube un poco la dificultad para comprender algo más cercano a un escenario de la vida real. Se emplearan **dos operaciones (métodos)** con sus respectivos mensajes de request y response, todos con distintos atributos integrados.

### 1. El archivo `.proto` (`ejemplo2_mensajes_multiples/universidad.proto`)

Aquí se diseña un servicio con **dos llamadas RPC**:
1. `ObtenerEstudiante`: Recibe un identificador numérico y devuelve datos de un estudiante.
2. `RegistrarEstudiante`: Recibe el nombre, la carrera y el semestre de un estudiante y devuelve una confirmación de la base de datos con su ID.

Fijese en cómo se usan diferentes tipos de datos, como `string`, `int32` o `bool`.

### 2. Compilando el código nuevamente

Para utilizar este diseño, se repite el paso de compilación ubicando nuestra terminal en la carpeta `ejemplo2_mensajes_multiples`:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. universidad.proto
```

### 3. Código del Servidor Universitario y Cliente de Casos de Uso

* En **`servidor.py`**: se implementan los dos métodos del protocolo. Además, se usa un diccionario (`dict`) básico para emular una "base de datos en la memoria". Este servidor devolverá errores reales en caso que alguien pida un estudiante que no tengamos registrado.
* En **`cliente.py`**: se programan tres pruebas automatizadas distintas para ver el éxito y el rechazo en el código.

**Probar:**
1. Al igual que antes, ejecuta el servidor en espera constante: `python servidor.py`.
2. Corre en otra terminal `python cliente.py` y asómbrate de cómo en milisegundos nuestro código interactúa mediante microservicios.

¡Sigue experimentando, editando los campos `.proto` y volviendo a compilar para agregar más tipos de datos a los estudiantes!
