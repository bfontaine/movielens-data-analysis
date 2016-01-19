#! /bin/bash

ohai() {
  echo "==> $*"
}

[ "$1" == "--reset" ] && {
  ohai "Resetting..."
  rm -rf data
}

if [ ! -d data ]; then
  ohai "Downloading the dataset"

  DATASET=ml-100k

  rm -f ${DATASET}.zip
  wget -q http://files.grouplens.org/datasets/movielens/${DATASET}.zip
  unzip -qq ${DATASET}.zip
  mv ${DATASET} data
  rm -f ${DATASET}.zip data/u*.base data/u*.test
fi
