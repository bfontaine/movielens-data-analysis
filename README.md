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

## Reset

If you want to import the database again, for example if you want to change the
dataset, just remove the `movies.db` file and run the import again.

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
