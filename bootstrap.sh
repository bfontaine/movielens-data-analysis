#! /bin/bash

ohai() {
  echo "==> $*"
}

[ "$1" == "--reset" ] && {
  shift
  ohai "Resetting the DB..."
  rm -f movies.db
}

if [ ! -d venv ]; then
  ohai "Initializing the Python environment"
  virtualenv venv >/dev/null

  curl -sL https://git.io/vguGk >| ./venv/bin/frameworkpython
  chmod +x ./venv/bin/frameworkpython
fi

ohai "Checking Python requirements"
venv/bin/pip install --disable-pip-version-check -qr requirements.txt

if [ ! -d data ]; then
  ohai "Downloading the dataset"

  DATASET=ml-100k

  rm -f ${DATASET}.zip
  wget -q http://files.grouplens.org/datasets/movielens/${DATASET}.zip
  unzip -qq ${DATASET}.zip
  mv ${DATASET} data
  rm -f ${DATASET}.zip data/u*.base data/u*.test
fi

if [ ! -f movies.db ]; then
  ohai "Importing in the DB"
  ./venv/bin/python scripts/import_data.py $*
fi

ohai "All done!"
