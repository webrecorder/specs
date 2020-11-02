#!/bin/bash
set -e

cd py-wacz
pytest -v --cov wacz -s
