#!/bin/bash -x

set -eo pipefail

if [[ "${ENV}" = "dev" ]]
then
    uvicorn --timeout-keep-alive 120 --host 0.0.0.0 --port 8080 app.main:app --reload
else
    uvicorn --timeout-keep-alive 120 --host 0.0.0.0 --port 8080 app.main:app
fi
