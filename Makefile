CXX=g++
CXX_FLAGS=-std=c++11 -O3

run: tictactoe.x
	./tictactoe.x
tictactoe.x: tictactoe.cpp
	$(CXX) $(CXX_FLAGS) $^ -o $@

clean:
	rm *.x
