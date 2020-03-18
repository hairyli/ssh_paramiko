# -*- coding: UTF-8 -*-
import os

def structure():
    filename = os.path.join(os.path.dirname(__file__), 'oss_per_stats.res').replace("\\", "/")
    with open(filename) as file_obj:
        contents = file_obj.read()
        print(contents.rstrip())

structure()
