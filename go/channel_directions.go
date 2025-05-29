package main

import "fmt"

func ping(pings chan<- string, msg string) {
	pings <- msg
}

func pong(pings <-chan string, pongs chan<- string) {
	msg := <-pings
	pongs <- msg
}

func main() {
	pings := make(chan string, 1)
	pongs := make(chan string, 1)
	ping(pings, "passed message")
	pong(pings, pongs)
	fmt.Println(<-pongs)
}

// This ping function only accepts a channel for sending values. It would be a
// compile-time error to try to receive on this channel.

// The pong function accepts one channel for receives (pings) and a second for
// sends (pongs).

// $ go run channel-directions.go
// passed message
