from src.tokenx import Class
from src.nodesx import *
from functools import wraps
import pickle

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.curr = tokens(0)
        self.prev = None

    def restorable(call):
        @wraps(call)
        def wrapper(self, *args, **kwargs):
            state = pickle.dumps(self.__dict__)
            result = call(self, *args, **kwargs)
            self.__dict__ = pickle.loads(state)
            return result

        return wrapper

    def eat(self, class_):
        if self.curr.class_ == class_:
            self.prev = self.curr
            self.curr = self.tokens.pop(0)
        else:
            self.die_type(class_.name, self.curr.class_.name)

    #program??
    def program(self):
        nodes = []
        while self.curr.class_ != Class.EOF:
            if self.curr.class_ == Class.VAR or self.curr.class_== Class.BEGIN or self.curr.class_ == Class.FUNCTION or self.curr.class_ == Class.PROCEDURE:
                nodes.append(self.decl())
            else:
                self.die_deriv(self.program.__name__)
         return Program(nodes)

    def id_(self):
        is_array_elem = self.prev.class_ != Class.TYPE #????
        id_ = Id(self.curr.lexeme)
        self.eat(Class.ID)
        if self.curr.class_ == Class.LPAREN and self.is_func_call():
            self.eat(Class.LPAREN)
            args = self.args()
            self.eat(Class.RPAREN)
            return FuncCall(id_, args)
        elif self.curr.class_ == Class.LBRACKET and is_array_elem:
            self.eat(Class.LBRACKET)
            index = self.expr()
            self.eat(Class.RBRACKET)
            id_ = ArrayElem(id_, index)
        if self.curr.class_ == Class.ASSIGN:
            self.eat(Class.ASSIGN)
            expr = self.expr()
            return Assign(id_, expr)
        else:
            return id_

    def decl(self):
        self.eat(Class.VAR)
        id_ = self.id_()
        if self.curr.class_ == Class.TWODOTS:
            self.eat(Class.TWODOTS)
            if self.curr.class_ == Class.ARRAY:
                min = None
                max = None
                elems = None
                self.eat(Class.ARRAY)
                self.eat(Class.LBRACKET)
                min = self.expr()
                self.eat(Class.DOT)
                self.eat(Class.DOT)
                max = self.expr()
                self.eat(Class.RBRACKET)
                self.eat(Class.OF)
                type_ = self.type_()
                if self.curr.class_ == Class.EQ:
                    self.eat(Class.EQ)
                    self.eat(Class.LPAREN)
                    elems = self.elems()
                    self.eat(Class.RPAREN)
                self.eat(Class.SEMICOLON)
                return ArrayDecl(type_, id_, min, max, elems)
            else:
                elems = None
                type_ = self.type_()
                self.eat(Class.SEMICOLON)
                return Decl(type_, id_, elems)
        elif self.curr.class_ == Class.COMMA:
            elems = self.elems()
            self.eat(Class.COMMA)
            type_ = self.type_()
            self.eat(Class.SEMICOLON)
            return Decl(type_, id_, elems)


    def fun_decl(self):
        if self.curr._class == Class.FUNCTION:
            self.eat(Class.FUNCTION)
            id_ = self.id_()
            self.eat(Class.LPAREN)
            params = self.params()
            self.eat(Class.RPAREN)
            self.eat(Class.TWODOTS)
            type_ = self.type_()
            self.eat(Class.SEMICOLON)
            self.eat(Class.BEGIN)
            block = self.block()
            self.eat(Class.END_BLOCK) #end block je end sa ;
            return FuncImpl(type_, id_, params, block)
        elif self.curr.class_ == Class.PROCEDURE:
            self.eat(Class.PROCEDURE)
            id_ = self.id_()
            self.eat(Class.LPAREN)
            params = self.params()
            self.eat(Class.RPAREN)
            self.eat(Class.SEMICOLON)
            self.eat(Class.BEGIN)
            block = self.block()
            self.eat(Class.END_BLOCK) #isto vazi
            return ProcImpl(id_, params, block)

    def block(self):
        nodes = []
        while self.curr.class_ != Class.END_BLOCK:
            if self.curr.class_ == Class.IF:
                nodes.append(self.if_())
            elif self.curr.class_ == Class.WHILE:
                nodes.append(self.while_())
            elif self.curr.class_ == Class.FOR:
                nodes.append(self.for_())
            elif self.curr.class_ == Class.BREAK:
                nodes.append(self.break_())
            elif self.curr.class_ == Class.CONTINUE:
                nodes.append(self.continue_())
            elif self.curr.class_ == Class.EXIT:
                nodes.append(self.exit_())
            elif self.curr.class_ == Class.TYPE:
                nodes.append(self.decl())
            elif self.curr.class_ == Class.ID:
                nodes.append(self.id_())
                self.eat(Class.SEMICOLON)
            else:
                self.die_deriv(self.block.__name__)
            return Block(nodes)

    def if_(self):
        self.eat(Class.IF)
        cond = self.logic()
        self.eat(Class.THEN)
        self.eat(Class.BEGIN)
        true = self.block()
        self.eat(Class.SIMPLE_END) ## zavisi da li ima else? ako nema onda je end block
        false = None
        if self.curr.class_ == Class.ELSE:
            self.eat(Class.ELSE)
            self.eat(Class.BEGIN)
            false = self.block()
            self.eat(Class.END_BLOCK)
        return If(cond, true, false)

    def while_(self):
        self.eat(Class.WHILE)
        cond = self.logic()
        self.eat(Class.DO)
        self.eat(Class.BEGIN)
        block = self.block()
        self.eat(Class.END_BLOCK)
        return While(cond, block)

    def for_(self):
        self.eat(Class.FOR)
        init = self.id_() ## assign ??? i:=1
        self.eat(Class.TO)
        maxNum = self.logic() # down to???? 3 - ide LOGIC
        self.eat(Class.DO)
        self.eat(Class.BEGIN)
        block = self.block()
        self.eat(Class.END_BLOCK)
        return For(init, maxNum, block)

    def factor(self): #nije dobar
        if self.curr.class_ == Class.INT:
            value = Int(self.curr.lexeme)
            self.eat(Class.INT)
            return value
        elif self.curr.class_ == Class.CHAR:
            value = Char(self.curr.lexeme)
            self.eat(Class.CHAR)
            return value
        elif self.curr.class_ == Class.STRING:
            value = String(self.curr.lexeme)
            self.eat(Class.STRING)
            return value
        elif self.curr.class_ == Class.ID:
            return self.id_()
        elif self.curr.class_ in [Class.MINUS, Class.NOT]:
            op = self.curr
            self.eat(self.curr.class_)
            first = None
            if self.curr.class_ == Class.LPAREN:
                self.eat(Class.LPAREN)
                first = self.logic()
                self.eat(Class.RPAREN)
            else:
                first = self.factor()
            return UnOp(op.lexeme, first)
        elif self.curr.class_ == Class.LPAREN:
            self.eat(Class.LPAREN)
            first = self.logic()
            self.eat(Class.RPAREN)
            return first
        elif self.curr.class_ == Class.SEMICOLON:
            return None
        else:
            self.die_deriv(self.factor.__name__)

    def term(self): #dobar
        first = self.factor()
        while self.curr.class_ in [Class.STAR, Class.DIV, Class.MOD]:
            if self.curr.class_ == Class.STAR:
                op = self.curr.lexeme
                self.eat(Class.STAR)
                second = self.factor()
                first = BinOp(op, first, second)
            elif self.curr.class_ == Class.DIV:
                op = self.curr.lexeme
                self.eat(Class.DIV)
                second = self.factor()
                first = BinOp(op, first, second)
            elif self.curr.class_ == Class.MOD:
                op = self.curr.lexeme
                self.eat(Class.MOD)
                second = self.factor()
                first = BinOp(op, first, second)
        return first

    def expr(self): #dobar
        first = self.term()
        while self.curr.class_ in [Class.PLUS, Class.MINUS]:
            if self.curr.class_ == Class.PLUS:
                op = self.curr.lexeme
                self.eat(Class.PLUS)
                second = self.term()
                first = BinOp(op, first, second)
            elif self.curr.class_ == Class.MINUS:
                op = self.curr.lexeme
                self.eat(Class.MINUS)
                second = self.term()
                first = BinOp(op, first, second)
        return first

    def compare(self): #dobar
        first = self.expr()
        if self.curr.class_ == Class.EQ:
            op = self.curr.lexeme
            self.eat(Class.EQ)
            second = self.expr()
            return BinOp(op, first, second)
        elif self.curr.class_ == Class.NEQ:
            op = self.curr.lexeme
            self.eat(Class.NEQ)
            second = self.expr()
            return BinOp(op, first, second)
        elif self.curr.class_ == Class.LT:
            op = self.curr.lexeme
            self.eat(Class.LT)
            second = self.expr()
            return BinOp(op, first, second)
        elif self.curr.class_ == Class.GT:
            op = self.curr.lexeme
            self.eat(Class.GT)
            second = self.expr()
            return BinOp(op, first, second)
        elif self.curr.class_ == Class.LTE:
            op = self.curr.lexeme
            self.eat(Class.LTE)
            second = self.expr()
            return BinOp(op, first, second)
        elif self.curr.class_ == Class.GTE:
            op = self.curr.lexeme
            self.eat(Class.GTE)
            second = self.expr()
            return BinOp(op, first, second)
        else:
            return first

    def logic(self): #dobar
        first = self.compare()
        if self.curr.class_ == Class.AND:
            op = self.curr.lexeme
            self.eat(Class.AND)
            second = self.compare()
            return BinOp(op, first, second)
        elif self.curr.class_ == Class.OR:
            op = self.curr.lexeme
            self.eat(Class.OR)
            second = self.compare()
            return BinOp(op, first, second)
        else:
            return first

    def params(self):
        params = []
        type_ = None #kako uzeti integer?
        while self.curr.class_ != Class.TWODOTS:
            if len(params) > 0:
                self.eat(Class.COMMA)
            id_ = self.id_()
            params.append(Decl(type_,id_))
        self.eat(Class.TWODOTS)
        type_ = self.type_()
        for x in params:
            x.type_=type_
        return Params(params)

    def elems(self):
        elems = []
        while self.curr.class_ != Class.TWODOTS:
            if len(elems) > 0 :
                self.eat(Class.COMMA)
            elems.append(self.expr())
        return Elems(elems)

    def args(self):
        args = []
        while self.curr.class_ != Class.RPAREN:
            if len(args) > 0:
                self.eat(Class.COMMA)
            args.append(self.expr())
        return Args(args)

    def break_(self):
        self.eat(Class.BREAK)
        self.eat(Class.SEMICOLON)
        return Break()

    def continue_(self):
        self.eat(Class.CONTINUE)
        self.eat(Class.SEMICOLON)
        return Continue()

    def exit_(self):
        self.eat(Class.EXIT)
        self.eat(Class.SEMICOLON)
        return Exit()

    def type_(self):
        type_ = Type(self.curr.lexeme)
        self.eat(Class.TYPE)
        return type_

    @restorable
    def is_func_call(self):
        try:
            self.eat(Class.LPAREN)
            self.args()
            self.eat(Class.RPAREN)
            return self.curr.class_ == Class.SEMICOLON
        except:
            return False

    def parse(self):
        return self.program()

    def die(self, text):
        raise SystemExit(text)

    def die_deriv(self, fun):
        self.die("Derivation error: {}".format(fun))

    def die_type(self, expected, found):
        self.die("Expected: {}, Found: {}".format(expected, found))



