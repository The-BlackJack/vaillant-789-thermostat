import re, copy

_tok = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+')


def parse(text):
    stack = [[]]
    for t in _tok.findall(text):
        if t == "(":
            stack.append([])
        elif t == ")":
            n = stack.pop()
            stack[-1].append(n)
        else:
            stack[-1].append(t)
    return stack[0]


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def unq(s):
    if s.startswith('"'):
        return s[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return s


def dump(n, ind=0):
    if not isinstance(n, list):
        return n
    simple = all(not isinstance(c, list) for c in n)
    if simple:
        return "(" + " ".join(n) + ")"
    parts = []
    head = []
    for c in n:
        if not isinstance(c, list) and not parts:
            head.append(c)
        else:
            parts.append(c)
    s = "(" + " ".join(head)
    for c in parts:
        s += "\n" + "\t" * (ind + 1) + dump(c, ind + 1)
    return s + "\n" + "\t" * ind + ")"


def find(n, key):
    for c in n:
        if isinstance(c, list) and c and c[0] == key:
            return c
    return None


def findall(n, key):
    return [c for c in n if isinstance(c, list) and c and c[0] == key]


class SymLib:
    cache = {}

    def __init__(self, path):
        if path not in SymLib.cache:
            with open(path, encoding="utf-8") as f:
                tree = parse(f.read())[0]
            SymLib.cache[path] = {unq(s[1]): s for s in findall(tree, "symbol")}
        self.syms = SymLib.cache[path]

    def flat(self, name):
        s = self.syms[name]
        ext = find(s, "extends")
        if not ext:
            return copy.deepcopy(s)
        parent_name = unq(ext[1])
        p = self.flat(parent_name)
        new = [p[0], q(name)]
        child_props = {unq(c[1]): c for c in findall(s, "property")}
        used = set()
        for c in p[2:]:
            if isinstance(c, list) and c[0] == "property":
                k = unq(c[1])
                if k in child_props:
                    new.append(copy.deepcopy(child_props[k])); used.add(k)
                else:
                    new.append(c)
            elif isinstance(c, list) and c[0] == "symbol":
                sub = unq(c[1])
                c = copy.deepcopy(c)
                c[1] = q(name + sub[len(parent_name):])
                new.append(c)
            else:
                new.append(c)
        # zusaetzliche Properties des Kindes vor die Untersymbole setzen
        extra = [copy.deepcopy(v) for k, v in child_props.items() if k not in used]
        idx = next(i for i, c in enumerate(new) if isinstance(c, list) and c[0] == "symbol")
        new[idx:idx] = extra
        return new


def pins_of(sym):
    """-> list of dict(number, name, type, x, y, angle, unit)"""
    out = []
    base = unq(sym[1]).split(":")[-1]
    for sub in findall(sym, "symbol"):
        nm = unq(sub[1])
        unit, style = [int(v) for v in nm[len(base) + 1:].split("_")]
        if style not in (0, 1):
            continue
        for p in findall(sub, "pin"):
            at = find(p, "at")
            out.append(dict(number=unq(find(p, "number")[1]), name=unq(find(p, "name")[1]),
                            type=p[1], x=float(at[1]), y=float(at[2]), angle=float(at[3]) if len(at) > 3 else 0.0,
                            unit=unit))
    return out
