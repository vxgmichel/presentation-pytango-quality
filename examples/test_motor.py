# Imports
import motor
from math import pi
from mock import Mock
from devicetest import DeviceTestCase, main


# Test case
class MotorTestCase(DeviceTestCase):

    device = motor.Motor
    properties = {'host': '10.10.10.10'}

    @classmethod
    def mocking(cls):
        cls.controller_cls = motor.MotorController = Mock()
        cls.controller = motor.MotorController.return_value
    
    def test_properties(self):
        self.controller_cls.assert_called_with('10.10.10.10:1234')
        
    def test_position(self):
        for deg, rad in [(0, 0), (-90, -pi/2), (90, pi/2)]:
            self.device.position = deg
            self.controller.write.assert_called_with(rad)
            self.controller.read.return_value = rad
            self.assertEquals(self.device.position, deg)


# Main execution
if __name__ == "__main__":
    main()
