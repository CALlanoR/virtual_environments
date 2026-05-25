package main

import (
	"fmt"
	"math"
)

// Go supports constants of character, string, boolean, and numeric values.
const s string = "constant"

func main() {
	fmt.Println("s: ", s)

	// A const statement can also appear inside a function body.
	const n = 500000000

	const d = 3e20 / n
	fmt.Println("d: ", d)

	fmt.Println("int64(d): ", int64(d))

	fmt.Println("math.Sin(n): ", math.Sin(n))
}
