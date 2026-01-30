#!/usr/bin/env python3
from multiprocessing import freeze_support

if __name__ == '__main__':
    freeze_support()
    from app import app
    app.run(host='0.0.0.0', port=5000)

