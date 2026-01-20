import string
from .chunk import chunkwise

_DIGITS = '0123456789'
_LETTERS = string.ascii_letters
_LETTERS_AND_DIGITS = string.ascii_letters + string.digits
_PRINTABLE1 = string.printable
_PRINTABLE2 = _PRINTABLE1 + ' '


def load_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        return load(f.read())


# noinspection PyUnresolvedReferences
def load(data: str):
    lines = []
    for ln in data.splitlines():
        if ln.rstrip():
            lines.append(ln.rstrip())
    
    def parse_dict_key():
        nonlocal flag
        x0, x1 = _analyze_line(
            ln1.lstrip() + '\n', 'GET_DICT_KEY', {'key': ''}
        )
        if x0 == 'dict_key':
            new_node = {}
            info['node'][x1] = new_node
            info['node'] = new_node
            info['node_chain'].append((_get_indent(ln2), new_node))
        elif x0 == 'kv_pair':
            info['node'][x1[0]] = x1[1]
            flag = 'IN_DICT_2'
        else:
            raise NotImplementedError
    
    result = None
    flag = 'INIT'
    info = {}
    
    for lnx, (ln0, ln1, ln2) in enumerate(chunkwise(lines, 3, 1)):
        if not ln1: continue
        # print(lnx, flag, '"{}"'.format(ln1), ':v')
        
        if flag == 'INIT':
            if ln1[0] == '-':
                raise NotImplementedError
            elif ln1[0] in _LETTERS:
                flag = 'IN_DICT'
                result = {}
                info['node'] = result
                info['node_chain'] = [(0, result)]
                parse_dict_key()
            else:
                raise NotImplementedError
        
        elif flag == 'IN_DICT':
            t0 = _get_initial_type(ln1.lstrip())
            if t0 == 'dict_or_string':
                parse_dict_key()
        
        elif flag == 'IN_DICT_2':
            indent = _get_indent(ln1)
            last_indent = info['node_chain'][-1][0]
            if indent > last_indent:
                raise E.UnreacableCase
            elif indent < last_indent:
                for i, (xindent, xnode) in enumerate(info['node_chain']):
                    if indent == xindent:
                        info['node'] = xnode
                        info['node_chain'] = info['node_chain'][:i + 1]
                        break
                else:
                    raise Exception(
                        'current indent should match one of the node chain'
                    )
            parse_dict_key()
        
    assert result is not None
    return result


def _analyze_line(text, flag, info):
    info = info or {}
    for tx, (t0, t1, t2) in enumerate(chunkwise(text, 3, 1)):
        # print(':v', flag, 'text[{}] = "{}"'.format(tx, t1))
        if flag == 'INIT':
            raise NotImplementedError
        elif flag == 'GET_DICT_KEY':
            if t1 == ':':
                if t2 == '\n':
                    return 'dict_key', info['key']
                else:
                    assert t2 == ' '
                    flag = 'GET_DICT_VALUE_1'
            elif t1 in _LETTERS_AND_DIGITS:
                info['key'] += t1
            else:
                raise NotImplementedError
        elif flag == 'GET_DICT_VALUE_1':
            if t1 != ' ':
                info['value'] = t1
                flag = 'GET_DICT_VALUE_2'
        elif flag == 'GET_DICT_VALUE_2':
            if t1 == '\n':
                return 'kv_pair', (
                    info['key'], _auto_convert_value_type(info['value'])
                )
            else:
                info['value'] += t1
        else:
            raise NotImplementedError
    raise E.UnreacableCase
    

def _auto_convert_value_type(value: str):
    if value == 'true':
        return True
    elif value == 'false':
        return False
    elif value == 'null':
        return None
    elif value.isdigit():
        return int(value)
    else:
        return value

        
def _get_indent(line):
    for i, char in enumerate(line):
        if char != ' ':
            return i
    raise Exception


def _get_initial_type(line):
    if line[0] == '#':
        return 'comment'
    elif line[0] == '-':
        return 'list'
    elif line[0] in _LETTERS:
        return 'dict_or_string'
    else:
        raise NotImplementedError


class E:
    class UnreacableCase(Exception):
        pass
