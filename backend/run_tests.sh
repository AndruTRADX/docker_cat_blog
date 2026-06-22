#!/bin/sh
pip install --no-cache-dir -r requirements.txt pytest
python -m pytest tests/ -v