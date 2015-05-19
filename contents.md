name: empty layout
layout: true

---
name: main title
class: center, middle

Software quality for PyTango Device Servers
===========================================

## Unit-testing, documentation and packaging

Vincent Michel - MAX IV - NEXEYA

TANGO Meeting 2015 - Krakow

[bit.do/pytango-quality](http://bit.do/pytango-quality)

???

Software quality for Python applied to TANGO DS

Unittesting with unittest and nose

Documentation with sphinx

Packaging with setuptools

***
---
name: unit testing layout
layout: true

1. Unit testing
===============

---
name: title 1
class: center, middle

**F**ast

**A**utomated

**I**solated

**R**epeatable

???

Fast: Unit tests should run fast and be run often

Automated: Unit tests should run fast and be run often

Isolated: Unit tests test small things

Repeatable: requires an independant and isolated environment

***
---
name: unit testing - problems

## Problems

- How to deal with the TANGO database?

  - Use --file option

???

run a local database from a file

***
--

- How to simulate hardware communication?

  - Mocking (python-mock)

???

Mocking external dependencies is what makes unit tests isolated

***
--

- How to simulate the client?

  - PyTango.DeviceProxy

???

That was an easy one

***
--

- How to handle both at the same time?

  - Threaded environment

???

Testing while running the device server in a separate thread

Makes it accessible
- from the inside (mocking and monkey patching)
- from the outside (device proxy)

=> accessing the device from both ends

***
---
name: unit testing - devicetest

## devicetest python library


- On github:

  - [vxgmichel/python-tango-devicetest](http://github.com/vxgmichel/python-tango-devicetest)

???

Feel free to fork it !

***
--

- Provides:

  - a context manager

  - a command line interface

  - a test case base class

???

Requirement: PyTango >= 8.1.1

Uses unittest module

***
--

- Includes:

  - A detailed README

  - A demo project

???

More complete than the presentation, so have a look at it!

***
---
name: unit-testing - example 1

## Example - PyTango device

```python
class Motor(Device):
    __metaclass__ = DeviceMeta

    host = device_property(dtype=str)

    def init_device(self):
        self.get_device_properties()
        self.controller = MotorController(self.host + ":1234") 
    
    position = attribute(dtype=float, access=AttrWriteType.READ_WRITE)

    def read_position(self):
        radian = self.controller.read()
        return math.degrees(radian)

    def write_position(self, value):
        radian = math.radians(value)
        self.controller.write(radian)
```

???

Simple device:

 - a host property used to initialize a motor controller (host + port)

 - a position attribute in degree

 - but the motor controller works with radians

 - convert angles using math.degree and math.radians

***
---
name: unit testing - example 2

## Example - Context manager and CLI

```python
>>> from devicetest import TangoTestContext
>>> from motor import Motor
>>> prop = {"host":"10.10.10.10"}
>>> with TangoTestContext(Motor, properties=prop) as proxy:
...     print proxy.position
```

Run the device `motor.Motor` locally
 - optional properties, port and debug level
 - compatible with old and new API

???

Context manager rocks!

Enter: start the server

Exit: kill the server 

Simple!

***
--

```bash
usr@machine:/~python-devicetest$ python -m devicetest motor.Motor
--prop "{'host':'10.10.10.10'}"
Ready to accept request
Motor started on port 55683 with properties {'host': '10.10.10.10'}.
Device access: localhost:55683/test/nodb/motor#dbase=no
Server access: localhost:55683/dserver/Motor/motor#dbase=no
```

???

CLI equivalent, displaying accesses for clients

***
---
name: unit testing - example 3

## Example - Test case

```python
class MotorTestCase(DeviceTestCase):

    device = motor.Motor
    properties = {'host': '10.10.10.10'}

    @classmethod
    def mocking(cls):
        cls.controller_cls = motor.MotorController = Mock()
        cls.controller = motor.MotorController.return_value
    
    def test_properties(self):
*       self.controller_cls.assert_called_with('10.10.10.10:1234')
        
    def test_position(self):
        for deg, rad in [(0, 0), (-90, -pi/2), (90, pi/2)]:
            self.device.position = deg
*           self.controller.write.assert_called_with(rad)
            self.controller.read.return_value = rad
*           self.assertEquals(self.device.position, deg)
```

???

Test case is set up using class attributes

2 tests, 3 assertions (highlighted)

Mocking: class method called before every tests

1 - Check proper controller instanciation

For three different angles:

2 - Check proper writing of attribute position

3 - Check proper reading of attribute position

The Init command is run between each tests

---
name: unit testing - example 4

## Example - Running the tests

Using nose:

```bash
$ nosetests test_motor --processes=1 --process-restartworker --verbose
```

???

nose: a test collector

processes=1: enable multiprocessing 

restartworker: use a different process for each test module

verbose: get a verbose output

***
--

Tests output:

```bash
test_position (test_motor.MotorTestCase) ... ok
test_properties (test_motor.MotorTestCase) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.043s

OK
```

???

Hourray, it passes!

And fast, 43 ms!

Can be easily automated

***
--

Tests could also include:

- commands, state machine, etc.

???

Obvisously, this was a simple device

But it works fine with more complex devices (scope device)

***
---
name: unit testing - results

### Results

 - Tests are independant as long as the `Init` command clears the device state

???

This should usually be the case (except for ALBA devices)

***
--

 - Works for devices using an internal thread

???

Requires more precaution, but works fine (scope device)

***
--

 - Quite fast: less than 100ms for simple test cases 

???

Up to a few seconds for big devices with inner thread

***
--

### Limitations

 - Using a test context twice will produce a segmentation fault

???

Known issue in PyTango, might be possible to use RestartServer once it is fixed

***
--

 - Properties cannot be changed between each test

???

Probably the biggest issue, even though it is possible to use several test modules

***
--

 - Tango events are not supported by the '--file' execution mode

???

Another big issue, see the documentation for more details, though it can be mocked 

***
--

 - Not compatible with the coverage tool "coverage"

???

Sooooo Sad! 

Coverage is great, but somehow, the tango layer messes up with its collector

***
---
name: documentation layout
layout: true

2. Documentation
===============

---
name: title 2
class: center, middle

Generating documentation from the code 

Sphinx extensions

???

Pogo can do it to, sure.

But still, sphinx has many interesting features.

---
name: documentation - sphinx presentation

### autodoc extension

 - build an html documentation from python docstrings

 - using directives in reStructuredText source files

???

Probably the most important extension of sphinx

Structure the documentation with rst files

But fetch the contents directly from the code

***
--

### devicedoc extension

 - Available on github

   - [vxgmichel/python-tango-devicedoc](http://github.com/vxgmichel/python-tango-devicedoc)

 - Includes:

  - A detailed README

  - A demo project

???

That extension recognizes TANGO object and adapt to generate the documentation

Again feel free to play with it!

***
---
name: documentation - example 1

## Example - PyTango Device

Documented motor device:

```python
class Motor(Device):
    """Motor device.

    Device states description:
*       - **ON**: the device is up and running
*       - **FAULT**: cannot connect to the controller
    """
    __metaclass__ = DeviceMeta

*   #: Can also be an IP address
    host = device_property(
        dtype=str,
        doc="Hostname of the motor.")

    [...]
```

???

First note: `rst` syntaxes inside docstrings

Second note: "hash + column" notation to add documentation to python attributes

***
---
name: documentation - example 2

## Example - PyTango Device

Adding a command:

```python
    [...]

    position = attribute(
        dtype=float,
*       unit="degrees",
        access=AttrWriteType.READ_WRITE,
        doc="Current position of the motor.")

    @command(
*       dtype_in=float, doc_in="angle in degrees",
*       dtype_out=float, doc_out="angle in radians")
    def radians(self, arg):
        """Convert the given angle from degrees to radians."""
        return math.radians(arg)

    [...]
```

???

Adding the unit to the position attribute arguments

Adding a command that converts a float to a float

***
---
name: documentation - example 3

## Example - Sphinx configuration

Configuration file: `conf.py`

```python
master_doc = 'index'
project = 'tango-device-motor'
copyright = '2015, Tango Controls'
extensions = ['sphinx.ext.autodoc', 'devicedoc']
```

???

Minimal configuration file

Includes metadata and settings

***
--

Source file: `index.rst`

```bash
.. automodule:: motor
    :members: Motor
```

???

Minimal `rst` file.

Using the `automodule` directive to generate the documentation for `motor.Motor`

***
--

Build documentation

```bash
sphinx-build docs/source docs/builds
```

???

A simple command to build the doc

source to destination

***
---
name: documentation view
template: empty layout
background-image: url(documentation.png)

???

So that's what we get.

Check all the docstrings out.

***
---
name: documentation - results

### Features

- More sphinx directive for customized documentation

???

Again, the scope project is a good example of that

See the README

***
--

- Possibility to automate builds (git hook, jenkins, etc.)

???

Or uploading on github pages

***
--

### Limitations

- Not compatible with the old PyTango API

???

And it's probably not gonna change

***
--

- Experimental, some syntaxes won't work as expected

???

Yep, sorry about that!

***
--

- Rigid implementation of headers and sections

???

Again, feel free to work on it!

***
---
name: packaging layout
layout: true

3. Packaging
============

---
name: title 2
class: center, middle

Package structure in python

`setup.py` as a Makefile

???

Most of it apply to all python packages

More repositories with smaller projects

---
name: packaging - package structure

## Package structure

Example with standard structure:

```bash
|- README.md
|- setup.py
|- setup.cfg
|- motor/
|    |- __init__.py
|    |- __main__.py
|    |- device.py
|    |- server.py
|- script/
|    |- Motor
|- test/
|    |- test_motor.py
|- docs/
|    |- source/
|    |     |- index.rst
|    |     |- conf.py
```

???

5 parts:

- setup for packaging

- package or packages 

- scripts to install

- unit tests

- documentation sources

***
---

#### `device.py` and `server.py`

Might interesting to:

- Split device and server in two modules

???

Helps to make the distinction

A matter of taste probably

***
--

- Get rid of the filename dependency to run the server:

  ```python
  from PyTango import server
  from motor.device import Motor

  SERVER_NAME = "Motor"

  def run(args=None, **kwargs):
      if not args:
          args = sys.argv[1:]
      args = [SERVER_NAME] + list(args)
      server.run((Motor,), args, **kwargs)
  
  if __name__ == "__main__":
      run()
  ```

???

Allows to run the server from anywhere

***
---

#### `__init__.py`

Make interesting objects visible at package level

```python
from motor.device import Motor
from motor.server import run
```

```python
>>> from motor import run
run(["instance_name"])
```

???

True for all python packages

Example: easily run the server from python interpreter

***
--

#### `__main__.py`

Take profit  of `-m` option

```python
from motor.server import run
run()
```

``` bash
$ python -m motor instance_name -v3
```

???

-m option: run the given library module as a script

`__main__.py` is called when running a package as a script

Won't work with python 2.6 and before

Example: easily run the server from the console 


***
---

#### `setup.py`

Metadata, packaging information and custom commands

```python
from setuptools import setup
from commands import UploadPages

setup(name="tangods-motor",
      version="0.1.0",
      description="Device server for a simple motor.",
      long_description=open("README.md").read(),
      packages=["motor"],
      scripts=["script/Motor"],
      test_suite="nose.collector",
      cmdclass={'upload_pages': UploadPages},
      )
```

#### `________`


See `distutils` and `setuptools` documentation for more information

???

`setup.py` includes:

- Metadata: name, version, descritpion

- Packaging: packages, script, test_suite

- Custom commands: here pusblish documentation on github pages 

***
---

#### `setup.cfg`

Add options for setup commands

```bash
[bdist_rpm]
requires = python-motorlib
build_requires = python-setuptools

[nosetests]
where = test
processes = 1 
process-restartworker = 1

[build_sphinx]
source-dir = docs/source
build-dir  = docs/build
```

#### `________`

See `distutils` and `setuptools` documentation for more information

???

Add options for:

- building rpm: dependencies

- unittesting: multiprocessing (cf first part)

- documentation: directories (cf second part)

***
---

## Usage

```bash
# Run server from package
$ python -m motor instance_name
# Install
$ python setup.py install
# Run server from script
$ Motor instance_name
# Tests
$ python setup.py nosetests
# Build docs 
$ python setup.py build_sphinx
# Upload documentation
$ python setup.py update_pages
# Build rpm
$ python setup.py bdist_rpm
```

A full example on github:

- [MaxIV-KitsControls/dev-maxiv-scope](https://github.com/MaxIV-KitsControls/dev-maxiv-scope)

???

Just listing previously seen commands

Have a look at the scope device repo

***
---
name: final
layout: false
class: center, middle

Questions ?
===========

___

Presentation written in `Markdown` and rendered by [remark](http://remarkjs.com/) slideshow tool

Sources for this presentation can be found on github

[vxgmichel/presentation-pytango-quality](https://github.com/vxgmichel/presentation-pytango-quality)

Thanks



