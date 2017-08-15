#include <mpi.h>
#include <stdio.h>

int main(int argc, char ** argv)
{
	int rank;
	int a[1000], b[500];
	MPI_Init(&argc, &argv);
	int status;
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	if (rank == 0) {
		MPI_Send(&a[500], 500, MPI_INT, 1, 0, MPI_COMM_WORLD);
		sort(a, 500);
		MPI_Recv(b, 500, MPI_INT, 1, 0, MPI_COMM_WORLD, &status);
		/* Serial: Merge array b and sorted part of array a */
	}
	else 
		if (rank == 1) {
			MPI_Recv(b, 500, MPI_INT, 0, 0, MPI_COMM_WORLD, &status);
			sort(b, 500);
			MPI_Send(b, 500, MPI_INT, 0, 0, MPI_COMM_WORLD);
		}
	MPI_Finalize(); 
	return 0;
}