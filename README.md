# scriptmerge: Convert Python packages into a single script

Scriptmerge can be used to convert a Python script and any Python modules
it depends on into a single-file Python script.
There are likely better alternatives depending on what you're trying to do.
For instance:

* If you want to create a single file that can be executed by a Python interpreter,
  use [zipapp](https://docs.python.org/3/library/zipapp.html).

* If you need to create a standalone executable from your Python script,
  I recommend using an alternative such as [PyInstaller](http://www.pyinstaller.org/).

Since scriptmerge relies on correctly analysing both your script and any dependent modules,
it may not work correctly in all circumstances.


## Installation

```sh
pip install scriptmerge
```

## Usage

You can tell scriptmerge which directories to search using the `--add-python-path` argument.
For instance:

```sh
scriptmerge scripts/blah --add-python-path . > /tmp/blah-standalone
```

Or to output directly to a file:

```sh
scriptmerge scripts/blah --add-python-path . --output-file /tmp/blah-standalone
```

You can also point scriptmerge towards a Python binary that it should use
sys.path from, for instance the Python binary inside a virtualenv:

```sh
scriptmerge scripts/blah --python-binary _virtualenv/bin/python --output-file /tmp/blah-standalone
```

Sscriptmerge cannot automatically detect dynamic imports,
but you can use `--add-python-module` to explicitly include modules:

```sh
scriptmerge scripts/blah --add-python-module blah.util
```

Scriptmerge can exclucde modules from be added to output.
This is useful in special cases where is it known that a module is not required to run the methods being used in the output.
An example might be a script that is being used as a LibreOffice macro.
You can use `--exclude-python-module` to explicitly exclude modules.

`--exclude-python-module` takes one or more regular expressions

In this example module `blah` is excluded entirly.
`blah\.*` matches modules such as `blah.__init__`, `blah.my_sub_module`.

```sh
scriptmerge scripts/blah --exclude-python-module blah\.*
```

By default, scriptmerge will ignore the shebang in the script
and use `"#!/usr/bin/env python"` in the output file.
To copy the shebang from the original script,
use `--copy-shebang`:

```sh
scriptmerge scripts/blah --copy-shebang --output-file /tmp/blah-standalone
```

Scritpmerge can strip all doc strings and comments from imported modules using the `--clean` option.

```sh
scriptmerge --clean
```

To see all scriptmerge options:

```sh
scriptmerge --help
```

As you might expect with a program that munges source files, there are a
few caveats:

* Due to the way that scriptmerge generates the output file, your script
  source file should be encoded using UTF-8. If your script doesn't declare
  its encoding in its first two lines, then it will be UTF-8 by default
  as of Python 3.

* Your script shouldn't have any ``from __future__`` imports.

* Anything that relies on the specific location of files will probably
  no longer work. In other words, ``__file__`` probably isn't all that
  useful.

* Any files that aren't imported won't be included. Static data that
  might be part of your project, such as other text files or images,
  won't be included.

# Credits

Scriptmerge is a fork of [stickytape](https://pypi.org/project/stickytape/).

Credit goes to Michael Williamson as the original author.
