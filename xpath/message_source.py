# stdlib
from ._compat import get_translator
from .exceptions import CompiletimeException
from .exceptions import RuntimeException
try:
    _ = get_translator("xpath")
except Exception:
    _ = str

ERRORNUMS = {1:1, 2:2, 3:3, 10: 10, 100: 100, 101: 101, 200:200}

from .exceptions import ERRORNUMS, ERRORCODES, CODES, CompiletimeException, RuntimeException

COMPILETIME = {num: ERRORNUMS.get(num) for num in (1,2,3) }
RUNTIME = {num: ERRORNUMS.get(num) for num in (1,10,100, 101, 200) }


