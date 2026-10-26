"""Build a record the lab parser will accept, and shorten CHR() chains.

A scanner that spells a short string as CHR(n)||CHR(n) can use up the whole
length budget before the query is finished. A quoted literal is the same
value and fits.
"""

import re

PREFIX = "v1|"
LENGTH_DIGITS = 4
MAX_BODY = 180

_CHR_CHAIN = re.compile(r"CHR\(\d+\)(?:\|\|CHR\(\d+\))*", re.I)


def collapse_chr(sql):
    def repl(match):
        chars = "".join(chr(int(number)) for number in re.findall(r"\d+", match.group(0)))
        return "'" + chars.replace("'", "''") + "'"

    return _CHR_CHAIN.sub(repl, sql)


def wrap(body):
    size = len(body.encode())
    if size > MAX_BODY:
        raise ValueError(f"body is {size} bytes; the lab accepts at most {MAX_BODY}")
    return f"{PREFIX}{size:0{LENGTH_DIGITS}X}|{body}"
