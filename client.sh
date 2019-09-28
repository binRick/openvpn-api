#!/bin/bash
cd $( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
set -e
source venv/bin/activate
python setup.py install >/dev/null 2>/dev/null
exec ./client.py 2>&1
