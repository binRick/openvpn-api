#!/bin/bash
cd $( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
set -e
source venv/bin/activate 2>/dev/null || {
	python3 -m venv venv && source venv/bin/activate
}
nodemon -w . -e py,json,yaml,sh -x ./client.py
