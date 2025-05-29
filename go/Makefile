hello:
	echo "Hello"

build_hello_world:
	go build -o bin/hello_world hello_world.go

build_vars:
	go build -o bin/vars vars.go

build_arrays:
	go build -o bin/arrays arrays.go

build_slices:
	go build -o bin/slices slices.go

build_slicing_slices:
	go build -o bin/slicing_slices slicing_slices.go

build_slices_copy:
	go build -o bin/slices_copy slices_copy.go

build_maps:
	go build -o bin/maps maps.go

run_hello_world:
	go run hello_world.go

compile:
	echo "Compiling for every OS and Platform"
	GOOS=linux GOARCH=arm go build -o bin/hello_world-linux-arm hello_world.go
	GOOS=linux GOARCH=arm64 go build -o bin/hello_world-linux-arm64 hello_world.go
	GOOS=freebsd GOARCH=386 go build -o bin/hello_world-freebsd-386 hello_world.go
	
all: build_hello_world vars arrays

clean:
	rm -rf bin/*
	rmdir bin