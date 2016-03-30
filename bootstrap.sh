#! /bin/bash

ohai() {
  echo "==> $*"
}

DATASET=ml-100k
DIRECTORY=data-$DATASET

if [ ! -d $DIRECTORY ]; then
  ohai "Downloading the dataset"

  rm -f ${DATASET}.zip
  wget -q http://files.grouplens.org/datasets/movielens/${DATASET}.zip
  unzip -qq ${DATASET}.zip
  mv $DATASET $DIRECTORY
  rm -f ${DATASET}.zip $DIRECTORY/u*.base $DIRECTORY/u*.test
fi

if [ ! -f movies.db ]; then
  ohai "Importing in the DB"
  ./venv/bin/python scripts/import_data.py $DIRECTORY $DATASET
fi

ohai "All done!"
