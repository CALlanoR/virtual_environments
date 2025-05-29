import grpc
import json
from concurrent import futures
import threading
import time

# gRPC definitions (replace with your actual protobuf and service definitions)
import example_pb2
import example_pb2_grpc

# Flask imports
from flask import Flask, jsonify

# --- Shared Message ---
SHARED_MESSAGE = "Hello from IoT Gateway"

# --- gRPC Server ---
class ExampleService(example_pb2_grpc.ExampleServiceServicer):
    def SayHello(self, request, context):
        return example_pb2.HelloReply(message=SHARED_MESSAGE)  # Use shared message

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    example_pb2_grpc.add_ExampleServiceServicer_to_server(ExampleService(), server)
    server.add_insecure_port('[::]:50051')  # gRPC port
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

# --- REST API Server (Flask) ---
app = Flask(__name__)

@app.route('/api/hello', methods=['GET'])
def hello_rest():
    return jsonify({"message": SHARED_MESSAGE})  # Use shared message

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404


def serve_rest():
    print('REST API server started on port 8000 (Flask)')
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)  # Disable reloader for threading


if __name__ == '__main__':
    # Start gRPC server in a separate thread
    grpc_thread = threading.Thread(target=serve_grpc)
    grpc_thread.start()

    # Start REST API server (Flask) in a separate thread
    rest_thread = threading.Thread(target=serve_rest)
    rest_thread.start()

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Shutting down servers...")


pip install grpcio protobuf


=============================

Create a file named example.proto (or whatever you prefer) with your gRPC service definition. Here's a very basic example:

      
syntax = "proto3";

package example;

service ExampleService {
  rpc SayHello (HelloRequest) returns (HelloReply);
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}

==============================

Generate gRPC code:

Use the grpc_tools.protoc tool to generate the Python code from your .proto file. This will create the example_pb2.py and example_pb2_grpc.py files that you import in the Python code.

      
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. example.proto

Make sure you run this command from the directory containing example.proto.

Replace Placeholders:

    Ensure the import example_pb2 and import example_pb2_grpc lines in the Python code correctly import the files generated in the previous step.

Run the Python code:

      
python your_script_name.py

    
============================== 

Test the gRPC service:

You'll need a gRPC client to test the gRPC service. Here's a basic Python gRPC client example:

      
import grpc
import example_pb2
import example_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = example_pb2_grpc.ExampleServiceStub(channel)
        response = stub.SayHello(example_pb2.HelloRequest(name='gRPC Client'))
    print("Greeter client received: " + response.message)

if __name__ == '__main__':
    run()

Save this as, for example, grpc_client.py and run it with python grpc_client.py. Make sure the server is running first. 

You should see something like: Greeter client received: Hello, gRPC Client from gRPC!

==============================

