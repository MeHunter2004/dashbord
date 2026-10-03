import os
import sys
from pathlib import Path

import uvicorn

from app.main import app


def main() -> None:
    if getattr(sys, 'frozen', False):
        os.chdir(Path(sys.executable).resolve().parent)
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')


if __name__ == '__main__':
    main()
