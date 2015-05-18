# Imports
import math
from PyTango import AttrWriteType
from StringIO import StringIO as MotorController
from PyTango.server import Device, DeviceMeta, device_property, attribute, run


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


# Main execution
if __name__ == "__main__":
    run((Motor,))
