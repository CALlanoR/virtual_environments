package main

import (
    "fmt"
    "maps"
)

func main() {

    m := make(map[string]int)

    m["k1"] = 7
    m["k2"] = 13

    fmt.Println("map:", m)

    r2, v1 := m["k1"]  // The optional second return value when getting a value from a map indicates if the key was present in the map. 
    fmt.Println("v1:", v1,  "r2: ", r2)

    r1, v3 := m["k3"]
    fmt.Println("v3:", v3, "r1: ", r1)

    fmt.Println("len:", len(m))

    delete(m, "k2")
    fmt.Println("map:", m)

    clear(m)
    fmt.Println("map:", m)

    r, prs := m["k2"]
    fmt.Println("prs:", prs, "r:", r)

    n := map[string]int{"foo": 1, "bar": 2}
    fmt.Println("map:", n)

    n2 := map[string]int{"foo": 1, "bar": 2}
    if maps.Equal(n, n2) {
        fmt.Println("n == n2")
    }
}

// $ go run maps.go 
// map: map[k1:7 k2:13]
// v1: 7
// v3: 0
// len: 2
// map: map[k1:7]
// map: map[]
// prs: false
// map: map[bar:2 foo:1]
// n == n2