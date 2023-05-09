CXX=g++
CXX_FLAGS=-std=c++11 -O3
JAVAC=javac
JAVA=java
RUSTC=rustc
RUSTC_FLAGS=-C lto=fat -C opt-level=3 -C codegen-units=1 -C overflow-checks=off -C panic=abort

all: tictactoe_rs.x tictactoe_cpp.x Play.class

run-rust: tictactoe_rs.x
	@./tictactoe_rs.x
	
run-cpp: tictactoe_cpp.x
	@./tictactoe_cpp.x

run-java: Play.class
	@$(JAVA) Play

tictactoe_rs.x: tictactoe.rs
	@$(RUSTC) $(RUSTC_FLAGS) $^ -o $@

tictactoe_cpp.x: tictactoe.cpp
	@$(CXX) $(CXX_FLAGS) $^ -o $@

Play.class: tictactoe.java
	@$(JAVAC) $^

clean:
	@rm -f *.x *.class
