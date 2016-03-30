#! /bin/bash -e

if [ "$#" -eq "0" ]; then
  echo "Usage:"
  echo "    $0 <dataset>"
  echo "<dataset> must be one of 'ml-100k', 'ml-1m', or 'ml-10m'."
  exit 1
fi

DATASET=$1
DIRECTORY=data-$DATASET

if [ ! -d $DIRECTORY ]; then
  echo "==> Downloading the dataset"

  rm -f ${DATASET}.zip
  URL=http://files.grouplens.org/datasets/movielens/${DATASET}.zip
  wget -q $URL -O ${DATASET}.zip
  unzip -qq -d .tmp ${DATASET}.zip
  # Sometimes the archive's directory has a different name, e.g. ml-10m.zip
  # unpacks in mk-10M100K. We use a temporary directory to be able to move
  # whatever directory it unpacks.
  mv .tmp/ml-* $DIRECTORY
  rm -rf .tmp
  rm -f ${DATASET}.zip $DIRECTORY/u*.base $DIRECTORY/u*.test
fi

if [ ! -f movies.db ]; then
  echo "==> Importing in the DB"
  ./venv/bin/python scripts/import_data.py $DIRECTORY $DATASET
fi

echo "==> All done!"
