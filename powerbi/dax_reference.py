"""Small, fail-closed interpreter for *this package's* DAX expression subset.

Not a Microsoft DAX engine. It checks expression semantics in tested single-
direction dimension filter contexts; it does not certify Desktop execution,
expanded tables, row context, RLS, engine collation or arbitrary DAX.
"""
import re

from pandas.api.types import is_numeric_dtype


TOKEN = re.compile(r"\s*(?:(--[^\n]*)(?:\n|$)|('(?:[^']|'')*')|(\[[^\]]+\])|"
                   r'("(?:[^"]|"")*")|([A-Za-z_][A-Za-z_0-9]*)|(\|\||[(),=\-]))')


class Parser:
    def __init__(self, text):
        self.tokens = []
        pos = 0
        while pos < len(text.rstrip()):
            match = TOKEN.match(text, pos)
            if not match:
                raise ValueError(f"Unsupported DAX token at: {text[pos:pos+50]!r}")
            pos = match.end()
            if match[1] is None:
                self.tokens.append(next(g for g in match.groups()[1:] if g is not None))
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self, token=None):
        found = self.peek()
        if found is None or (token is not None and found != token):
            raise ValueError(f"Expected {token}, found {found}")
        self.pos += 1
        return found

    def expression(self, level=0):
        operators = [('||',), ('=',), ('-',)]
        if level == len(operators):
            return self.primary()
        node = self.expression(level + 1)
        while self.peek() in operators[level]:
            op = self.take()
            node = ('binary', op, node, self.expression(level + 1))
        return node

    def primary(self):
        token = self.take()
        if token == 'VAR':
            assignments = []
            while True:
                name = self.take()
                self.take('=')
                assignments.append((name, self.expression()))
                if self.peek() != 'VAR':
                    break
                self.take('VAR')
            self.take('RETURN')
            return ('variables', assignments, self.expression())
        if token.startswith("'"):
            table = token[1:-1].replace("''", "'")
            if (self.peek() or '').startswith('['):
                return ('column', table, self.take()[1:-1])
            return ('table', table)
        if token.startswith('['):
            return ('measure', token[1:-1])
        if token.startswith('"'):
            return ('literal', token[1:-1].replace('""', '"'))
        if self.peek() == '(':
            self.take('(')
            args = []
            if self.peek() != ')':
                args.append(self.expression())
                while self.peek() == ',':
                    self.take(',')
                    args.append(self.expression())
            self.take(')')
            return ('call', token, args)
        return ('variable', token)

    def parse(self):
        node = self.expression()
        if self.peek() is not None:
            raise ValueError(f"Unparsed DAX: {self.tokens[self.pos:]}")
        return node


def parse_measures(text):
    """One named measure per unindented 'Name =' line; comments ignored."""
    clean = re.sub(r'--[^\n]*', '', text)
    headers = list(re.finditer(r'^([^\n=]+)\s=\s*$', clean, re.M))
    result = {}
    for i, match in enumerate(headers):
        name = match[1].strip()
        if name in result:
            raise ValueError(f"Duplicate measure: {name}")
        end = headers[i+1].start() if i+1 < len(headers) else len(clean)
        expression = clean[match.end():end].strip()
        result[name] = {'expression': expression, 'ast': Parser(expression).parse()}
    if not result or clean[:headers[0].start()].strip():
        raise ValueError('No measures or unexpected preamble')
    return result


FUNCTIONS = {'SUM': 1, 'DISTINCTCOUNT': 1, 'DIVIDE': 2, 'CALCULATE': None,
             'REMOVEFILTERS': 1, 'ISBLANK': 1, 'BLANK': 0, 'IF': 3}


def validate_bindings(measures, tables):
    dependencies = {}

    def visit(node, variables, deps):
        kind = node[0]
        if kind in {'table', 'column'}:
            if node[1] not in tables:
                raise ValueError(f'Unknown table: {node[1]}')
            if kind == 'column' and node[2] not in tables[node[1]]:
                raise ValueError(f'Unknown column: {node[1]}[{node[2]}]')
        elif kind == 'measure':
            if node[1] not in measures:
                raise ValueError(f'Unknown measure: {node[1]}')
            deps.add(node[1])
        elif kind == 'variable':
            if node[1] not in variables:
                raise ValueError(f'Unknown variable: {node[1]}')
        elif kind == 'variables':
            local = set(variables)
            for name, expr in node[1]:
                visit(expr, local, deps)
                local.add(name)
            visit(node[2], local, deps)
        elif kind == 'binary':
            visit(node[2], variables, deps)
            visit(node[3], variables, deps)
        elif kind == 'call':
            name, args = node[1:]
            if name not in FUNCTIONS or (FUNCTIONS[name] is not None and len(args) != FUNCTIONS[name]):
                raise ValueError(f'Unsupported function/arity: {name}')
            if name == 'CALCULATE' and len(args) < 2:
                raise ValueError('CALCULATE requires the reviewed filters')
            if name in {'SUM', 'DISTINCTCOUNT'} and args[0][0] != 'column':
                raise ValueError(f'{name} requires a column reference')
            if name == 'REMOVEFILTERS' and args[0][0] != 'table':
                raise ValueError('REMOVEFILTERS supports whole dimension tables here')
            for arg in args:
                visit(arg, variables, deps)
            if name == 'SUM' and not is_numeric_dtype(tables[args[0][1]][args[0][2]]):
                raise ValueError('SUM requires a numeric column')
    for name, measure in measures.items():
        deps = set()
        visit(measure['ast'], set(), deps)
        dependencies[name] = deps

    def acyclic(name, path):
        if name in path:
            raise ValueError(f'Cyclic DAX measure dependency: {name}')
        for dep in dependencies[name]:
            acyclic(dep, path | {name})
    for name in measures:
        acyclic(name, set())


def selected(table_name, context, tables, relationships):
    """Direct single-direction dimension filtering; no implicit fact-row filters."""
    frame = tables[table_name]
    mask = frame.index.to_series().map(lambda _: True)
    for (table, col), values in context.items():
        if table == table_name:
            mask &= frame[col].isin(values)
    for rel in relationships:
        if rel['to_table'] == table_name:
            dim = rel['from_table']
            if any(t == dim for t, _ in context):
                allowed = selected(dim, context, tables, [])[rel['from_column']]
                mask &= frame[rel['to_column']].isin(allowed)
    return frame[mask]


def evaluate(name, measures, context, tables, relationships):
    """Return None for BLANK. Deliberately rejects unimplemented expression forms."""
    def expr(node, ctx, variables):
        kind = node[0]
        if kind == 'measure':
            return expr(measures[node[1]]['ast'], ctx, {})
        if kind == 'literal':
            return node[1]
        if kind == 'variable':
            return variables[node[1]]
        if kind == 'variables':
            local = dict(variables)
            for var, expression in node[1]:
                local[var] = expr(expression, ctx, local)
            return expr(node[2], ctx, local)
        if kind == 'binary':
            left, right = expr(node[2], ctx, variables), expr(node[3], ctx, variables)
            if node[1] == '||':
                return bool(left) or bool(right)
            if node[1] == '-':
                return (left or 0) - (right or 0)
            raise ValueError('Equality supported only in CALCULATE filters')
        if kind != 'call':
            raise ValueError(f'Unsupported scalar node: {node}')
        func, args = node[1:]
        if func in {'SUM', 'DISTINCTCOUNT'}:
            _, table, col = args[0]
            frame = selected(table, ctx, tables, relationships)
            if frame.empty:
                return None
            return int(frame[col].sum()) if func == 'SUM' else int(frame[col].nunique())
        if func == 'CALCULATE':
            modified = dict(ctx)
            # Filter modifiers applied before explicit column filters.
            for arg in args[1:]:
                if arg[:2] == ('call', 'REMOVEFILTERS'):
                    table = arg[2][0][1]
                    modified = {key: value for key, value in modified.items() if key[0] != table}
                elif arg[:2] != ('binary', '='):
                    raise ValueError('Unsupported CALCULATE filter')
            for arg in args[1:]:
                if arg[:2] == ('binary', '='):
                    _, table, col = arg[2]
                    modified[(table, col)] = {expr(arg[3], ctx, variables)}
            return expr(args[0], modified, variables)
        if func == 'BLANK':
            return None
        if func == 'ISBLANK':
            return expr(args[0], ctx, variables) is None
        if func == 'IF':
            return expr(args[1] if expr(args[0], ctx, variables) else args[2], ctx, variables)
        if func == 'DIVIDE':
            numerator, denominator = [expr(a, ctx, variables) for a in args]
            return None if numerator is None or denominator in (None, 0) else numerator / denominator
        raise ValueError(f'Unsupported scalar call: {func}')
    return expr(measures[name]['ast'], context, {})
