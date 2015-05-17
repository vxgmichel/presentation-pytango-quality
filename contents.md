name: main title
class: center, middle

Software quality for PyTango Device Servers
===========================================

## Unit-testing, documentation and packaging

Vincent Michel - MAX IV - NEXEYA

TANGO Meeting 2015 - Krakow

---
name: title 1
class: center, middle

1. Unit testing
===============

Fast

Automated

Isolated

Repeatable

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

--

- How to simulate hardware communication?

  - Mocking (python-mock)

--

- How to simulate the client?

  - PyTango.DeviceProxy

--

- How to handle both at the same time?

  - Threaded environment

---

name: Unit testing - devicetest
template: Unit testing

## devicetest python library


- On github:

  - [vxgmichel/python-tango-devicetest](http://github.com/vxgmichel/python-tango-devicetest)

--

- Provides:

  - a context manager
  - a command line interface
  - a test case base class

--

- Includes:
  - A detailed README
  - A demo project

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

--

```bash
usr@machine:/~python-devicetest$ python -m devicetest motor.Motor
--prop "{'host':'10.10.10.10'}"
Ready to accept request
Motor started on port 10001 with properties {'host': '10.10.10.10'}.
Device access: localhost:10001/test/nodb/motor#dbase=no
Server access: localhost:10001/dserver/Motor/motor#dbase=no
```

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
        cls.controller_cls = motor.MotorController = Mock(name="MotorController")
        cls.controller = motor.MotorController.return_value
    
    def test_properties(self):
        self.controller_cls.assert_called_with('10.10.10.10:1234')
        
    def test_position(self):
        for deg, rad in [(0, 0) (-90, -pi/2), (90, pi/2)]:
            self.device.position = deg
            self.controller.write.assert_called_with(rad)
            self.controller.read.return_value = rad
            self.assertEquals(self.device.position, deg)

```

---
name: Unit testing - example 4
template: Unit testing

## Example - Running the test

```bash
$ nosetests test_directory --process-restartworker --processes=1
```

Output:

```bash
PASTE OUTPUT HERE
```

---
name: Unit testing - 
template: Unit testing

### Results

 - Tests are independant as long as the `Init` command clears the device state

--

 - Quite fast: less than 100ms for simple test cases 

--

 - Works for devices using an internal thread

--

### Limitations

 - Using a test context twice will produce a segmentation fault

--

 - Properties cannot be changed at runtime

--

 - Tango events are not supported by the '--file' execution mode

--

 - Not compatible with the coverage tool "coverage"



