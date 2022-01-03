#!/bin/bash

gnome-terminal -- bash -c "cd uap/src && python3 uap.py; exec bash"
docker-compose down -v && docker-compose build && docker-compose up