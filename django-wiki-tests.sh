#!/bin/bash

git clone https://github.com/django-wiki/django-wiki /django-wiki
pip3 install hatch
cd /django-wiki && hatch run test:all