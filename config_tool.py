import importlib
from functools import lru_cache
@lru_cache(maxsize=128)
def read_single_conf_lru_cache(arg):
    try: r = getattr(importlib.import_module('config_private'), arg)
    except: r = getattr(importlib.import_module('config'), arg)
    return r

def get_conf(*args):
    # 建议您复制一个config_private.py放自己的秘密, 如token, 避免不小心传github被别人看到
    res = []
    for arg in args:
        r = read_single_conf_lru_cache(arg)
        res.append(r)
    return res
def get_free_port():
    """
        返回当前系统中可用的未使用端口。
    """
    import socket
    from contextlib import closing
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]