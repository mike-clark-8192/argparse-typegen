import ast

CAPTURE_VAR = '__argparse_typegen_val_'

class TransformLastAssignable(ast.NodeTransformer):
    def visit_Module(self, node):
        self.generic_visit(node)
        # Find the last expression or assignment statement that is assignable
        last_assignable = None
        for n in reversed(node.body):
            if isinstance(n, (ast.Assign, ast.Expr)):
                last_assignable = n
                break
        if last_assignable:
            if isinstance(last_assignable, ast.Expr):
                self.transform_expr(node, last_assignable)
            elif isinstance(last_assignable, ast.Assign):
                self.transform_assign(last_assignable)
            else:
                raise ValueError("Unexpected type of last assignable statement")
        else:
            raise ValueError(f"No assignable statement found in code:\n{code}")
        return node

    def transform_assign(self, assignable: ast.Assign):
        assignable.targets.append(ast.Name(id=CAPTURE_VAR, ctx=ast.Store()))
        assignable.targets[-1].lineno = assignable.lineno
        assignable.targets[-1].col_offset = assignable.col_offset

    def transform_expr(self, node: ast.Module, assignable: ast.Expr):
        new_node = ast.Assign(
                    targets=[ast.Name(id=CAPTURE_VAR, ctx=ast.Store())],
                    value=assignable.value
                )
        new_node.lineno = assignable.lineno
        new_node.col_offset = assignable.col_offset
        new_node.targets[0].lineno = assignable.lineno
        new_node.targets[0].col_offset = assignable.col_offset
        node.body.append(new_node)

def execeval(code):
    """
    Execute Python `code` and return the value of the last assignable expression or statement.
    """
    tree = ast.parse(code)

    # print indented AST tree:
    # import astor
    # print(astor.dump_tree(tree))

    # Transform the AST tree to capture the value of the last assignable expression or statement
    transformer = TransformLastAssignable()
    transformed_tree = transformer.visit(tree)
    
    # display AST source code:
    # import astor
    # print(astor.to_source(transformed_tree))

    # Execute the transformed code
    compiled_code = compile(transformed_tree, filename="<ast>", mode="exec")
    exec_context = {}
    exec(compiled_code, exec_context)

    # Return the value of the captured variable
    captured_value = exec_context[CAPTURE_VAR]
    return captured_value

if __name__ == "__main__":
    # Example usage
    code = """
import sys
foo = sys.path
list(reversed(foo))
    """
    print(execeval(code))
