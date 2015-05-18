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
name: title 1
class: center, middle

1. Unit testing
===============

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
name: Unit testing
layout: true

1. Unit testing
===============

---
name: Unit testing - problems
template: Unit testing

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

name: Unit testing - devicetest
template: Unit testing

## devicetest python library


- On github:

  - [vxgmichel/python-tango-devicetest](http://github.com/vxgmichel/python-tango-devicetest)

???

Fell free to fork it !

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
name: Unit-testing - example 1
template: Unit testing

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
name: Unit testing - example 2
template: Unit testing

## Example - context manager and CLI

```python
>>> from devicetest import TangoTestContext
>>> from motor import Motor
>>> prop = {"host":"10.10.10.10"}
>>> with TangoTestContext(Motor, properties=prop) as proxy:
...     print proxy.position
```

Run the device `MyServer.MyDevice` locally
 - optional properties, port and debug level
 - compatible with old and new API

???

Context manager rocks!

Enter: start the server

Exit:  kill ther server 

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
name: Unit testing - example 3
template: Unit testing

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
name: Unit testing - example 4
template: Unit testing

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
name: Unit testing - results
template: Unit testing

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

