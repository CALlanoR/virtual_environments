## Documentation
https://www.grpc.io/

## Example of grpc.io
# Clone the repository to get the example code:
$ git clone -b v1.33.1 https://github.com/grpc/grpc
# Navigate to the "hello, world" Python example:
$ cd grpc/examples/python/helloworld


in examples/python

python3.7 -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/helloworld.proto

create greeter_server.py

create greeter_client.py

Run the server:
$ python greeter_server.py

From another terminal, run the client:
$ python greeter_client.py

==========================================================================

With kotlin:

cd examples/grpc-kotlin/examples

./gradlew installDist

./server/build/install/server/bin/hello-world-server

From another terminal, run the python client:
python3.7 greeter_client.py   # remove SayHelloAgain of proto file

https://developers.google.com/protocol-buffers/docs/overview