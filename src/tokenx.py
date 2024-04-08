from enum import Enum, auto

class Class(Enum):
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    DIV = auto()
    MOD = auto()

    BEGIN = auto()
    DOT = auto()
    END_PROGRAM = auto()
    END_BLOCK = auto()

    OR = auto()
    AND = auto()
    NOT = auto()
    XOR = auto()

    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()

    ASSIGN = auto()
    TWODOTS = auto()
    SEMICOLON = auto()
    COMMA = auto()

    VAR = auto()
    TYPE = auto()
    CHAR = auto()
    INT = auto()
    STRING = auto()
    REAL = auto()
    BOOL = auto()

    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    REPEAT = auto()
    UNTIL = auto()
    DO = auto()
    TO = auto()

    BREAK = auto()
    CONTINUE = auto()
    EXIT = auto()

    PROCEDURE = auto()
    FUNCTION = auto()
    ARRAY = auto()
    OF = auto()

    THEN = auto()
    SIMPLE_END = auto()

    ID = auto()
    EOF = auto()

class Token:
    def __init__(self, class_, lexeme):
        self.class_ = class_
        self.lexeme = lexeme

    def __str__(self):
        return "<{} {}>".format(self.class_, self.lexeme)
