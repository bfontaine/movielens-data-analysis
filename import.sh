#! /bin/bash

if [ "$#" -eq "0" ]; then
  echo "Usage:"
  echo "    $0 <dataset>"
  echo "<dataset> must be 'ml-100k' for now."
  exit 1
fi

DATASET=$1
DIRECTORY=data-$DATASET

if [ ! -d $DIRECTORY ]; then
  echo "==> Downloading the dataset"

  rm -f ${DATASET}.zip
  wget -q http://files.grouplens.org/datasets/movielens/${DATASET}.zip
  unzip -qq ${DATASET}.zip
  mv $DATASET $DIRECTORY
  rm -f ${DATASET}.zip $DIRECTORY/u*.base $DIRECTORY/u*.test
fi

if [ ! -f movies.db ]; then
  echo "==> Importing in the DB"
  ./venv/bin/python scripts/import_data.py $DIRECTORY $DATASET
fi

echo "==> All done!"
