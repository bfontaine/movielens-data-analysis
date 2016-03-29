# ***REMOVED*** - MovieLens

## Setup

    ./boostrap.sh

This will setup the environment as well as retrieve the data for you.

## Troubleshooting

On OS X if you get an error when using Matplotlib use
`./venv/bin/frameworkpython` instead of `./venv/bin/python`.

## Report

The report is located under `report/`; it can be compiled with `./compile.sh`.
You might need to run `tlmgr install csquotes` so that it can find the module.
If you have `fswatch` you can use `./watch.sh` to re-compile the report
every time a source file changes.
