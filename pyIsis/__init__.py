# -*- coding: utf-8 -*-

#from .conn import *
#from .client import *

import os

__all__ = ['client','connection','utils','filesystem']
__author__ = "Sylvain Maziere"
__license__ = "GPL"
__maintainer__ = "Sylvain Maziere"
__email__ = "sylvain@predat.fr"
__status__ = "Development"

__version__ = 'unknown'
with open(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),'VERSION'),'rb') as fp:
    __version__ = fp.read().strip()

from connection import Client

