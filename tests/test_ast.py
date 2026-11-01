from ast_nodes import Binary, Literal


expression = Binary(
    left=Literal(10.0),
    operator="+",
    right=Literal(20.0)
)

print(expression)