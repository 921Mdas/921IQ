#!/bin/bash
uvicorn Main:app --host 0.0.0.0 --port $PORT
