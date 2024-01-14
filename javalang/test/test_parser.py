import unittest

from .. import parser, tokenizer, tree
from ..tokenizer import Position


class TestParser(unittest.TestCase):
    def test_parse_literal(self):
        parser = get_parser("12")
        literal = parser.parse_literal()
        self.assertIsInstance(literal, tree.Literal)
        self.assertEqual(literal.value, "12")
        self.assertEqual(literal.position, Position(1, 1))
        self.assertEqual(literal.end_position, Position(1, 2))

    def test_parse_par_expression(self):
        parser = get_parser("(x + y)")
        par_expression = parser.parse_par_expression()
        self.assertIsInstance(par_expression, tree.BinaryOperation)
        self.assertEqual(par_expression.position, Position(1, 1))
        self.assertEqual(par_expression.end_position, Position(1, 7))

    def test_parse_this(self):
        parser = get_parser("this")
        this = parser.parse_primary()
        self.assertIsInstance(this, tree.This)
        self.assertEqual(this.position, Position(1, 1))
        self.assertEqual(this.end_position, Position(1, 4))

        parser = get_parser("this()")
        this = parser.parse_primary()
        self.assertIsInstance(this, tree.ExplicitConstructorInvocation)
        self.assertEqual(this.position, Position(1, 1))
        self.assertEqual(this.end_position, Position(1, 6))

        parser = get_parser("this(1, 2)")
        this = parser.parse_primary()
        self.assertIsInstance(this, tree.ExplicitConstructorInvocation)
        self.assertEqual(len(this.arguments), 2)
        self.assertEqual(this.position, Position(1, 1))
        self.assertEqual(this.end_position, Position(1, 10))

    def test_parse_creator(self):
        parser = get_parser("new A()")
        class_creator = parser.parse_primary()
        self.assertIsInstance(class_creator, tree.ClassCreator)
        self.assertEqual(class_creator.position, Position(1, 1))
        self.assertEqual(class_creator.end_position, Position(1, 7))

        parser = get_parser("new int[] {1, 2, 3}")
        array_creator = parser.parse_primary()
        self.assertIsInstance(array_creator, tree.ArrayCreator)
        self.assertEqual(array_creator.position, Position(1, 1))
        self.assertEqual(array_creator.end_position, Position(1, 19))

    def test_parse_identifier(self):
        parser = get_parser("com.example.Person")
        identifier = parser.parse_primary()
        self.assertIsInstance(identifier, tree.MemberReference)
        self.assertEqual(identifier.position, Position(1, 1))
        self.assertEqual(identifier.end_position, Position(1, 18))

        parser = get_parser("com.example.Person.foo()")
        identifier = parser.parse_primary()
        self.assertIsInstance(identifier, tree.MethodInvocation)
        self.assertEqual(identifier.position, Position(1, 1))
        self.assertEqual(identifier.end_position, Position(1, 24))

    def test_parse_primitive_array_class_reference(self):
        parser = get_parser("int[].class")
        ref = parser.parse_primary()
        self.assertIsInstance(ref, tree.ClassReference)
        self.assertEqual(ref.position, Position(1, 1))
        self.assertEqual(ref.end_position, Position(1, 11))

    def test_parse_void_class_reference(self):
        parser = get_parser("void.class")
        ref = parser.parse_primary()
        self.assertIsInstance(ref, tree.VoidClassReference)
        self.assertEqual(ref.position, Position(1, 1))
        self.assertEqual(ref.end_position, Position(1, 10))

    def test_parse_interface_declaration(self):
        parser = get_parser("interface A {}")
        interface = parser.parse_type_declaration()
        self.assertIsInstance(interface, tree.InterfaceDeclaration)
        self.assertEqual(interface.position, Position(1, 1))
        self.assertEqual(interface.end_position, Position(1, 14))

    def test_parse_enum_declaration(self):
        parser = get_parser("enum A {}")
        interface = parser.parse_type_declaration()
        self.assertIsInstance(interface, tree.EnumDeclaration)
        self.assertEqual(interface.position, Position(1, 1))
        self.assertEqual(interface.end_position, Position(1, 9))

    def test_parse_local_variable_declaration(self):
        parser = get_parser("int x = 1;")
        local_var = parser.parse_local_variable_declaration_statement()
        self.assertIsInstance(local_var, tree.LocalVariableDeclaration)
        self.assertEqual(local_var.position, Position(1, 1))
        self.assertEqual(local_var.end_position, Position(1, 10))
        var = local_var.declarators[0]
        self.assertIsInstance(var, tree.VariableDeclarator)
        self.assertEqual(var.position, Position(1, 5))
        self.assertEqual(var.end_position, Position(1, 9))
        literal = var.initializer
        self.assertIsInstance(literal, tree.Literal)
        self.assertEqual(literal.position, Position(1, 9))
        self.assertEqual(literal.end_position, Position(1, 9))

        parser = get_parser("int x = {1, 2, 3};")
        local_var = parser.parse_local_variable_declaration_statement()
        self.assertIsInstance(local_var, tree.LocalVariableDeclaration)
        self.assertEqual(local_var.position, Position(1, 1))
        self.assertEqual(local_var.end_position, Position(1, 18))
        initializer = local_var.declarators[0].initializer
        self.assertIsInstance(initializer, tree.ArrayInitializer)
        self.assertEqual(initializer.position, Position(1, 9))
        self.assertEqual(initializer.end_position, Position(1, 17))

    def test_parse_catch_clause(self):
        parser = get_parser("catch (Exception e) {}")
        catch_clause = parser.parse_catch_clause()
        self.assertIsInstance(catch_clause, tree.CatchClause)
        self.assertEqual(catch_clause.position, Position(1, 1))
        self.assertEqual(catch_clause.end_position, Position(1, 22))

    def test_parse_binary_operation(self):
        parser = get_parser("x + (y * z);")
        binary_operation = parser.parse_expression()
        self.assertIsInstance(binary_operation, tree.BinaryOperation)
        self.assertEqual(binary_operation.position, Position(1, 1))
        self.assertEqual(binary_operation.end_position, Position(1, 11))


def get_parser(code: str) -> parser.Parser:
    return parser.Parser(tokenizer.tokenize(code))


if __name__ == "__main__":
    unittest.main()
