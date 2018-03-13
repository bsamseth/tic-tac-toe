CXX=g++
CXX_FLAGS=-std=c++11 -O3
JAVAC=javac
JAVA=java

all: tictactoe.x Play.class

run-cpp: tictactoe.x
	@./tictactoe.x

run-java: Play.class
	@$(JAVA) Play

tictactoe.x: tictactoe.cpp
	@$(CXX) $(CXX_FLAGS) $^ -o $@

Play.class: tictactoe.java
	@$(JAVAC) $^

clean:
	@rm -f *.x *.class
