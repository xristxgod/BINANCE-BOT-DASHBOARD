import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "DB")

BASE_ADDITION = os.path.join(ROOT_DIR, "addition")
BASE_FUTURESBOARD = os.path.join(ROOT_DIR, "futuresboard")

BASE_FILE = os.path.join(BASE_ADDITION, "files")
BASE_STATIC = os.path.join(BASE_FUTURESBOARD, "static")