# -*- coding: utf-8 -*-

def getSize(bytes):
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}iB"

        bytes /= 1024
