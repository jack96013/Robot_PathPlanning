'''
Author: TZU-CHIEH, HSU
Mail: j.k96013@gmail.com
Department: ECIE Lab, NTUT
Date: 2024-06-06 09:11:19
LastEditTime: 2024-06-14 15:46:32
Description: 
'''
import os
from configparser import ConfigParser

current_path = os.path.dirname(os.path.abspath(__file__))

parser = ConfigParser()

parser.read(f'{current_path}\config.ini')