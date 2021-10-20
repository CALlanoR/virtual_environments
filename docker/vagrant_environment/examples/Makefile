CC=gcc

%.o: %.c
	$(CC) -c -o $@ $<
allfork: fork00 fork01 fork02 fork03 fork04 fork05 fork06 fork07 fork08 fork09 fork10 fork11 fork12 fork13
allmessage: message_sender01 message_sender02 message_receiver message_sender03_multiplemessages message_receiver02_multiplemessages.c
allnamepipes: pipe_writer01 pipe_writer02 pipe_reader01 pipe_reader02 ordinary_pipe
all: allfork allmessage shared_memory_set01 shared_memory_get01 allnamepipes socket_client socket_server

fork00: fork00.o
	gcc -o fork00 fork00.o

fork01: fork01.o
	gcc -o fork01 fork01.o

fork02: fork02.o
	gcc -o fork02 fork02.o

fork03: fork03.o
	gcc -o fork03 fork03.o

fork04: fork04.o
	gcc -o fork04 fork04.o

fork05: fork05.o
	gcc -o fork05 fork05.o

fork06: fork06.o
	gcc -o fork06 fork06.o

fork07: fork07.o
	gcc -o fork07 fork07.o

fork08: fork08.o
	g++ -o fork08 fork08.cc

fork09: fork09.o
	gcc -o fork09 fork09.o

fork10: fork10.o
	gcc -o fork10 fork10.o

fork11: fork11.o
	gcc -o fork11 fork11.o

fork12: fork12.o
	g++ -o fork12 fork12.cc

fork13: fork13.o
	gcc -o fork13 fork13.o

shared_memory_set01: shared_memory_set01.o
	gcc -o shared_memory_set01 shared_memory_set01.o -lrt

shared_memory_get01: shared_memory_get01.o
	gcc -o shared_memory_get01 shared_memory_get01.o -lrt

shared_memory_set02: shared_memory_set02.o
	gcc -o shared_memory_set02 shared_memory_set02.o -lrt

shared_memory_get02: shared_memory_get02.o
	gcc -o shared_memory_get02 shared_memory_get02.o -lrt

message_sender01: message_sender01.o
	gcc -o message_sender01 message_sender01.o -lrt

message_sender02: message_sender02.o
	gcc -o message_sender02 message_sender02.o -lrt

message_receiver: message_receiver.o
	gcc -o message_receiver message_receiver.o -lrt

message_sender03_multiplemessages: message_sender03_multiplemessages.o
	gcc -o message_sender03_multiplemessages message_sender03_multiplemessages.o -lrt

message_receiver02_multiplemessages: message_receiver02_multiplemessages.o
	gcc -o message_receiver02_multiplemessages message_receiver02_multiplemessages.o -lrt

pipe_writer01: pipe_writer01.o
	gcc -o pipe_writer01 pipe_writer01.o

pipe_writer02: pipe_writer02.o
	gcc -o pipe_writer02 pipe_writer02.o

pipe_reader01: pipe_reader01.o
	gcc -o pipe_reader01 pipe_reader01.o

pipe_reader02: pipe_reader02.o
	gcc -o pipe_reader02 pipe_reader02.o

ordinary_pipe: ordinary_pipe.o
	gcc -o ordinary_pipe ordinary_pipe.o

socket_client: socket_client.o
	gcc -o socket_client socket_client.o
	
socket_server: socket_server.o
	gcc -o socket_server socket_server.o

tar:
	tar cf ../examples.tar . 
	mv ../examples.tar .
	
clean:
	rm -f *.o fork00 fork01 fork02 fork03 fork04 fork05 fork06 fork07 fork08 fork09 fork10 fork11 fork12 fork13
	rm -f shared_memory_set01 shared_memory_get01 shared_memory_get02 shared_memory_set02 
	rm -f message_receiver message_sender01 message_sender02 message_receiver02_multiplemessages message_sender03_multiplemessages
	rm -f pipe_reader02 pipe_reader01 pipe_writer01 pipe_writer02 ordinary_pipe 
	rm -f socket_client socket_server
	rm *.class