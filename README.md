# ***REMOVED*** - MovieLens

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

    ./import.sh ml-100k

Only the `ml-100k` dataset is supported for now. The script downloads the
archive, unpacks it in `data-ml-100k/`, and imports it in the DB.

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

## Report

The report is located under `report/`; it can be compiled with `./compile.sh`.
You might need to run `tlmgr install csquotes` so that it can find the module.
If you have `fswatch` you can use `./watch.sh` to re-compile the report
every time a source file changes.
