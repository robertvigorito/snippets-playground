import os as _os
from pathlib import Path as _Path


test_path = "/home/robert-v/dev/snippets-playground/pyproject.toml"


test_path_path = _Path(test_path)


joined_path = _os.path.join(test_path, "test")