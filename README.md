# scriptmerge

Convert Python packages into a single script as a standalone `.py` file or a `.pyz` file.

Scriptmerge can be used to convert a Python script and any Python modules
it depends on into a single-file Python script.

If you want output to be a `.py` file can use the `compilepy` command which outputs a `.py` file.
If you want output to be a `.pyz` file can use the `compilepyz` command which outputs a `.pyz` file.

The `.pyz` is a [zipapp](https://docs.python.org/3/library/zipapp.html) `.pyz` file.
It is recommended to use the `.pyz` file as it is a more modern way to distribute Python applications and it is faster to build and to load.

I also recommend checking out [PyInstaller](http://www.pyinstaller.org/).

Since scriptmerge relies on correctly analyzing both your script and any dependent modules,
it may not work correctly in all circumstances.

## Documentation

See the [documentation](https://github.com/Amourspirit/python-scriptmerge/wiki/) for more information.


## Installation

```sh
pip install scriptmerge
```

## Usage

You can tell scriptmerge which directories to search using the `--add-python-path` argument.
For instance:

```sh
scriptmerge compilepyz scripts/blah --add-python-path . > /tmp/blah-standalone
```

Or to output directly to a file:

```sh
scriptmerge compilepy scripts/blah --add-python-path . --output-file /tmp/blah-standalone
```

You can also point scriptmerge towards a Python binary that it should use
sys.path from, for instance the Python binary inside a virtualenv:

```sh
scriptmerge compilepyz scripts/blah --python-binary _virtualenv/bin/python --output-file /tmp/blah-standalone
```

Scriptmerge cannot automatically detect dynamic imports,
but you can use `--add-python-module` to explicitly include modules:

```sh
scriptmerge compilepyz scripts/blah --add-python-module blah.util
```

Scriptmerge can exclucde modules from be added to output.
This is useful in special cases where is it known that a module is not required to run the methods being used in the output.
An example might be a script that is being used as a LibreOffice macro.
You can use `--exclude-python-module` to explicitly exclude modules.

`--exclude-python-module` takes one or more regular expressions

In this example module `blah` is excluded entirly.
`blah\.*` matches modules such as `blah.__init__`, `blah.my_sub_module`.

```sh
scriptmerge compilepyz scripts/blah --exclude-python-module blah\.*
```

By default, scriptmerge will ignore the shebang in the script
and use `"#!/usr/bin/env python3"` in the output file.
To copy the shebang from the original script,
use `--copy-shebang`:

```sh
scriptmerge compilepy scripts/blah --copy-shebang --output-file /tmp/blah-standalone
```

Scritpmerge can strip all doc strings and comments from imported modules using the `--clean` option.

```sh
scriptmerge --clean
```

Scriptmerge by default will output a `.py` file. If you want to output a `.pyz` file, use the `--pyz-out` flag.

```sh
scriptmerge compilepy scripts/blah --pyz-out --output-file /tmp/blah-standalone.pyz
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

* When using `compilepy` Your script shouldn't have any ``from __future__`` imports.

* Anything that relies on the specific location of files will probably
  no longer work. In other words, ``__file__`` probably isn't all that
  useful.

* Any files that aren't imported won't be included. Static data that
  might be part of your project, such as other text files or images,
  won't be included.

# Credits

Scriptmerge is a fork of [stickytape](https://pypi.org/project/stickytape/).

Credit goes to Michael Williamson as the original author.
