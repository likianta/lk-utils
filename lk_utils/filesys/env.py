import os
import sys
import typing as t

IS_PYTHON_312_OR_HIGHER = sys.version_info >= (3, 12)
IS_PYTHON_314_OR_HIGHER = sys.version_info >= (3, 14)
IS_WINDOWS = os.name == 'nt'

system_privileged: t.Optional[bool] = None
#   None: unknown; True: yes; False: no.
