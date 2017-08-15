Examples
========

mpi_hello.c
===========
Change directory to your mirror folder and write this MPI helloworld program in a file mpi_hello.c 

Compile it:

mpiu@ub0:~$ mpicc mpi_hello.c -o mpi_hello

and run it (the parameter next to -n specifies the number of processes to spawn and distribute among nodes):

mpiu@ub0:~$ mpiexec -n 8 -f /home/mpiu/machinefile ./mpi_hello

You should now see output similar to this:

Hello from processor 0 of 8
Hello from proceessor 1 of 8
Hello from processor 2 of 8
Hello from processor 3 of 8
Hello from processor 4 of 8
Hello from processor 5 of 8
Hello from processor 6 of 8
Hello from processor 7 of 8

thread_level_support.c
======================
mpicc thread_level_support.c -o thread_level_support
mpiexec ./thread_level_support
Query thread level= 3  Init_thread level= 3

Explaination:
MPI_THREAD_SINGLE - Level 0: Only one thread will execute.

MPI_THREAD_FUNNELED - Level 1: The process may be multi-threaded, but only the main thread will make MPI calls - all MPI calls are funneled to the main thread.

MPI_THREAD_SERIALIZED - Level 2: The process may be multi-threaded, and multiple threads may make MPI calls, but only one at a time. That is, calls are not made concurrently from two distinct threads as all MPI calls are serialized.

MPI_THREAD_MULTIPLE - Level 3: Multiple threads may call MPI with no restrictions. 