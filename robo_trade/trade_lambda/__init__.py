#Auto-populate relative import.
import os
import pkgutil
__all__ = list(module for _, module, _ in pkgutil.iter_modules([os.path.dirname(__file__)]))

#Theres no pythonpath for lambda, so hack to make both relative imports and upstream dependencies work.
import sys
if 'requirements.txt' not in os.listdir(os.getcwd()):
    sys.path.append("../..")