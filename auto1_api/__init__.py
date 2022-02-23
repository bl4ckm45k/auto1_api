"""
:authors: bl4ckm45k
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2022 bl4ckm45k
"""

import sys
if sys.version_info < (3, 7):
    raise ImportError('Your Python version {0} is not supported, please install '
                      'Python 3.7+'.format('.'.join(map(str, sys.version_info[:3]))))

from .base import BaseApi
from .api import check_result, make_request, Methods
from .exceptions import (NetworkError, APIError, CartException, TeaPot)

__author__ = 'bl4ckm45k'
__version__ = '0.1.1'
__email__ = 'nonpowa@gmail.com'