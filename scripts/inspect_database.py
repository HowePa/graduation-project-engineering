"""Strict parser for the Golden Example CREATE TABLE subset, not a general SQL parser."""
import re
from common import cli, config, evidence, resolve

ID = r'`?([A-Za-z_][A-Za-z0-9_]*)`?'

def split_sql(text, separator=','):
    parts, start, depth, quote, i = [], 0, 0, None, 0
    while i < len(text):
        c = text[i]
        if quote:
            if c == quote:
                if i + 1 < len(text) and text[i+1] == quote:
                    i += 2
                    continue
                quote = None
            elif c == '\\':
                i += 2
                continue
        elif c in "'\"`":
            quote = c
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif c == separator and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1
        if depth < 0:
            raise ValueError('Unbalanced SQL parentheses')
        i += 1
    if quote or depth:
        raise ValueError('Unterminated SQL string or parentheses')
    parts.append(text[start:].strip())
    return [x for x in parts if x]


def names(text):
    result = []
    for item in split_sql(text):
        match = re.fullmatch(ID, item)
        if not match:
            raise ValueError(f'Unsupported index or key expression: {item}')
        result.append(match[1])
    return result


def parse(text):
    # Golden DDL intentionally excludes SQL comments and ALTER/CREATE INDEX statements.
    tables = []
    for stmt in split_sql(text, ';'):
        m = re.fullmatch(r'CREATE\s+TABLE\s+' + ID + r'\s*\((.*)\)\s*(?:ENGINE=InnoDB\s*)?(?:DEFAULT CHARSET=utf8mb4\s*)?(?:COMMENT=\'((?:[^\']|\'\')*)\'\s*)?', stmt, re.I | re.S)
        if not m:
            raise ValueError(f'Unsupported DDL; refusing partial extraction: {stmt[:100]}')
        table = {'name': m[1], 'comment': m[3], 'columns': [], 'foreign_keys': [], 'indexes': []}
        primary = []
        for entry in split_sql(m[2]):
            pk = re.fullmatch(r'PRIMARY KEY\s*\((.+)\)', entry, re.I)
            fk = re.fullmatch(r'(?:CONSTRAINT\s+`?\w+`?\s+)?FOREIGN KEY\s*\((.+?)\)\s+REFERENCES\s+' + ID + r'\s*\((.+?)\)', entry, re.I)
            idx = re.fullmatch(r'(UNIQUE\s+)?(?:KEY|INDEX)\s+' + ID + r'\s*\((.+)\)', entry, re.I)
            if pk:
                if primary: raise ValueError('Duplicate primary key')
                primary = names(pk[1]); continue
            if fk:
                table['foreign_keys'].append({'columns': names(fk[1]), 'references_table': fk[2], 'references_columns': names(fk[3])}); continue
            if idx:
                table['indexes'].append({'name': idx[2], 'columns': names(idx[3]), 'unique': bool(idx[1])}); continue
            col = re.fullmatch(ID + r'\s+(BIGINT|INT|VARCHAR|TEXT|DATETIME|TIMESTAMP|DECIMAL|BOOLEAN)(?:\(([^)]+)\))?(.*)', entry, re.I | re.S)
            if not col:
                raise ValueError(f'Unsupported column: {entry}')
            tail = col[4].strip()
            flags = {'nullable': True, 'primary_key': False, 'default': None, 'comment': None}
            while tail:
                token = re.match(r"^(NOT NULL|NULL|PRIMARY KEY|AUTO_INCREMENT|DEFAULT\s+(?:'(?:[^']|'')*'|NULL|CURRENT_TIMESTAMP|[-+]?\d+(?:\.\d+)?)|COMMENT\s+'(?:[^']|'')*')(?:\s+|$)", tail, re.I)
                if not token: raise ValueError(f'Unsupported column modifier: {tail}')
                term = token[1]; upper = term.upper()
                if upper == 'NOT NULL': flags['nullable'] = False
                elif upper == 'PRIMARY KEY': flags['primary_key'] = True; flags['nullable'] = False
                elif upper.startswith('DEFAULT '): flags['default'] = term[8:]
                elif upper.startswith('COMMENT '): flags['comment'] = term[9:-1].replace("''", "'")
                tail = tail[token.end():].strip()
            table['columns'].append({'name': col[1], 'type': col[2].upper(), 'length': col[3], **flags})
        cols = [c['name'] for c in table['columns']]
        if not cols or len(cols) != len(set(cols)): raise ValueError('Empty or duplicate columns')
        if primary and any(c['primary_key'] for c in table['columns']): raise ValueError('Multiple primary key declarations')
        for column in table['columns']:
            if column['name'] in primary: column.update(primary_key=True, nullable=False)
        for key in primary + [c for idx in table['indexes'] for c in idx['columns']] + [c for fk in table['foreign_keys'] for c in fk['columns']]:
            if key not in cols: raise ValueError(f'Unknown key column: {key}')
        tables.append(table)
    if not tables or len({t['name'] for t in tables}) != len(tables): raise ValueError('Empty or duplicate tables')
    by_name = {t['name']: t for t in tables}
    for table in tables:
        for fk in table['foreign_keys']:
            referenced = by_name.get(fk['references_table'])
            if referenced is None or set(fk['references_columns']) - {c['name'] for c in referenced['columns']} or len(fk['columns']) != len(fk['references_columns']):
                raise ValueError('Invalid foreign key')
    return tables


def run(root):
    root = root.resolve()
    cfg, _ = config(root)
    path = resolve(root, cfg['paths']['database']) / 'schema.sql'
    evidence(root, 'database', {'origin': 'ddl', 'tables': parse(path.read_text(encoding='utf-8'))}, [path],
             limitations=['DDL only; no live MySQL metadata comparison performed.'])

if __name__ == '__main__':
    cli(run)
