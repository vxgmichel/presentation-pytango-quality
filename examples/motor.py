# Imports
import math
from PyTango import AttrWriteType
from StringIO import StringIO as MotorController
from PyTango.server import Device, DeviceMeta, run
from PyTango.server import device_property, attribute, command 

# Motor device
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

# Motor device (documented version)
class Motor(Device):
    """ Motor device.

    Device states description:
        - **ON**: the device is up and running
        - **FAULT**: cannot connect to the controller
    """
    __metaclass__ = DeviceMeta

    #: Can also be an IP address
    host = device_property(
        dtype=str,
        doc="Hostname of the motor.")

    position = attribute(
        dtype=float,
        unit="degrees",
        access=AttrWriteType.READ_WRITE,
        doc="Current position of the motor.")

    @command(
        dtype_in=float, doc_in="angle in degrees",
        dtype_out=float, doc_out="angle in radians")
    def radians(self, arg):
        """Convert the given angle from degrees to radians."""
        return math.radians(arg)

    def init_device(self):
        self.get_device_properties()
        self.controller = MotorController(self.host + ":1234") 

    def read_position(self):
        radian = self.controller.read()
        return math.degrees(radian)

    def write_position(self, value):
        radian = math.radians(value)
        self.controller.write(radian)




# Main execution
if __name__ == "__main__":
    run((Motor,))
