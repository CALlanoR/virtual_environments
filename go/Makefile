hello:
	echo "Hello"

build_hello_world:
	go build -o bin/hello_world hello_world.go

run_hello_world:
	go run hello_world.go

compile:
	echo "Compiling for every OS and Platform"
	GOOS=linux GOARCH=arm go build -o bin/hello_world-linux-arm hello_world.go
	GOOS=linux GOARCH=arm64 go build -o bin/hello_world-linux-arm64 hello_world.go
	GOOS=freebsd GOARCH=386 go build -o bin/hello_world-freebsd-386 hello_world.go
	
all: build_hello_world

clean:
	rm -rf bin/*
	rmdir bin