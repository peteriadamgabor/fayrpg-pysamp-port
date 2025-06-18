#!/bin/bash

start_py="server_manager.py"

echo Clearing "${SRV:?}" folder
rm -rf "${SRV:?}"/*

echo Copy Open.mp files from "${OMP}" to "${SRV:?}"
cp -rf "${OMP}"/. "${SRV}"

echo Copy mode files from "${MOD}" to "${SRV:?}"
cp -rf "${MOD}"/. "${SRV}"

echo Enter to "${SRV:?}"
cd "${SRV:?}" || exit

echo install pip libs from requirements.txt
pip install -r ./requirements.txt

if [ -f "$start_py" ]; then
  echo Starting the serever with "${start_py}"
  python3.12 "${start_py}"
else
  echo Starting the serever with ./omp-server
  ./omp-server
fi
