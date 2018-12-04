# -*- coding: utf-8 -*-
# @Time    : 18-5-29 下午1:34
# @Author  : BlvinDon
# @Email   : wenbingtang@hotmail.com
# @File    : Function.py
# @Software: PyCharm
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False