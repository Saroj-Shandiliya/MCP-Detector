import ast
from typing import List
from ..result import Indicator
from .base import BaseScanner
from ..utils import logger

class ASTScanner(BaseScanner):
    def scan(self, file_path: str, content: str) -> List[Indicator]:
        indicators = []
        if file_path.endswith(".py"):
            try:
                tree = ast.parse(content)
                analyzer = PythonAnalyzer()
                analyzer.visit(tree)
                
                for imp in analyzer.imports:
                    indicators.append(Indicator(type="ast_import", value=imp, file=file_path))
                
                for cls in analyzer.classes:
                    indicators.append(Indicator(type="ast_class", value=cls, file=file_path))
                    
            except SyntaxError:
                logger.debug(f"Syntax error parsing {file_path}")
            except Exception as e:
                logger.warning(f"AST parse error {file_path}: {e}")
                
        # Future: Add JS parser using other tools
        return indicators

class PythonAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = []
        self.classes = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        self.classes.append(node.name)
        # Check base classes too
        self.generic_visit(node)
