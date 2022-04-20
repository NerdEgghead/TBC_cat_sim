#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import multiprocessing
from ui.ui import UI

u = UI()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    u.run_server()
