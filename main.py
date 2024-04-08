from src.lexerx import Lexer
from src.token import Class, Token
from src.parser import Parser
from src.grapherx import Grapher
import graphviz

def main():

    path = 'res/test2.pas'

    with open(path, 'r') as source:
        text = source.read()

        lexer = Lexer(text)
        tokens = lexer.lex()

        for f in tokens:
            print(f)



if __name__ == '__main__':
    main()
