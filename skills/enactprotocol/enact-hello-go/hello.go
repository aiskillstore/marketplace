package main

import (
	"fmt"
	"os"
	"runtime"
)

func main() {
	name := "World"
	if len(os.Args) > 1 {
		name = os.Args[1]
	}
	fmt.Printf("Hello, %s! 🐹\n", name)
	fmt.Printf("Go version: %s\n", runtime.Version())
}
