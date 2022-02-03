# add root-dir to sys path for tests
import sys

from os.path import abspath
from os.path import dirname as d

parent_dir = f"{d(d(abspath(__file__)))}"
sys.path.append(parent_dir)
