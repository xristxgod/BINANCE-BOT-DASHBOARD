from __future__ import annotations
import pathlib
import futuresboard.app
from futuresboard.config import Config
config = Config.from_config_dir(pathlib.Path.cwd() / "futures_board/config")

app = futuresboard.app.init_app(config)
