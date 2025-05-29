package main

import "fmt"

func main() {
	arr := [5]int{1, 2, 3, 4, 5}
	for i := 0; i < len(arr); i++ {
		fmt.Println(arr[i])
	}
	
	for index, value := range arr {
		fmt.Printf("Index: %d, Value: %d\n", index, value)
	}

	// Inicialización
	matrix := [3][3]int{
		{1, 2, 3},
		{4, 5, 6},
		{7, 8, 9},
	}

	// Acceso a elementos
	fmt.Println(matrix[0][1])  // Imprime: 2


	arr2 := [5]int{1, 2, 3, 4, 5}
	modifyArray(&arr2)
	fmt.Println(arr2[0])  // Imprime: 10

}

func modifyArray(arr *[5]int) {
	arr[0] = 10
}