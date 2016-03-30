# MovieLens Data Analysis

This repo contains code exported from a research project that uses the
[MovieLens 100k dataset](http://grouplens.org/datasets/movielens/). You can’t
do much of it without the context but it can be useful as a reference for
various code snippets.

The project is not endorsed by the University of Minnesota or the GroupLens
Research Group.

The original README follows.

-------------------------------------------------------------------------------

## Setup

Create your local Python environment with:

    virtualenv venv
    ./venv/bin/pip install --disable-pip-version-check -r requirements.txt

This will setup the environment as well as retrieve the data for you.

If in the future you want to add another `pip` package install it with:

    ./venv/bin/pip install <the-package>

Then make sure it’s added to the dependencies:

    ./venv/bin/pip freeze >| requirements.txt

## Import

    ./import.sh <dataset>

`<dataset>` can be one of `ml-100k`, `ml-1m`, or `ml-10m`. The script downloads
the archive, unpacks it in `data-<dataset>/`, and imports it in the DB.

You can only have one dataset in the DB at once; if you want to switch between
multiple ones you'll need to move the DB somewhere else, import another dataset
then rename the files around to switch.

## Reset

If you want to reset the database, for example to change the dataset, just
remove the `movies.db` file and run the import again.

## Troubleshooting

On OS X if you get an error when using Matplotlib use
`./venv/bin/frameworkpython` instead of `./venv/bin/python`.

Install it with:

  curl -sL https://git.io/vguGk >| ./venv/bin/frameworkpython
  chmod +x ./venv/bin/frameworkpython
