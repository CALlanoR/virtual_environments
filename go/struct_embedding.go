package main

import "fmt"

type base struct {
	num int
}

func (b base) describe() string {
	return fmt.Sprintf("base with num=%v", b.num)
}

type container struct {
	base
	str string
}

// When creating structs with literals, we have to initialize the embedding
// explicitly; here the embedded type serves as the field name.

func main() {

	// A container embeds a base. An embedding looks like a field without a name.
	co := container{
		base: base{
			num: 1,
		},
		str: "some name",
	}

	fmt.Printf("co={num: %v, str: %v}\n", co.num, co.str)

	fmt.Println("also num:", co.base.num)

	fmt.Println("describe:", co.describe())

	type describer interface {
		describe() string
	}

	var d describer = co
	fmt.Println("describer:", d.describe())
}

// $ go run struct-embedding.go
// co={num: 1, str: some name}
// also num: 1
// describe: base with num=1
// describer: base with num=1
