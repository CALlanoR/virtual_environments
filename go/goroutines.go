package main

import (
	"fmt"
	"time"
)

func f(from string) {
	for i := 0; i < 3; i++ {
		fmt.Println(from, ":", i)
	}
}

func main() {

	f("direct")

	go f("goroutine")

	go func(msg string) {
		fmt.Println(msg)
	}("going")

	time.Sleep(time.Second)
	fmt.Println("done")
}

// To invoke this function in a goroutine, use go f(s). This new goroutine will
// execute concurrently with the calling one.

// Our two function calls are running asynchronously in separate goroutines now.
// Wait for them to finish (for a more robust approach, use a WaitGroup).

// $ go run goroutines.go
// direct : 0
// direct : 1
// direct : 2
// goroutine : 0
// going
// goroutine : 1
// goroutine : 2
// done
