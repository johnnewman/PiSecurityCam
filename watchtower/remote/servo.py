from .microcontroller_comm import MicrocontrollerComm

class Servo:
    """
    Class used to represent one servo attached to a microcontroller. An
    instance of Servo can be used to tell the microcontroller to move the 
    servo to the on or off position.
    """

    def __init__(self,
                 angle_on: int,
                 angle_off: int,
                 controller: MicrocontrollerComm):
        
        super(Servo, self).__init__()
        self.__angle_on = angle_on
        self.__angle_off = angle_off
        self.__controller = controller

    def enable(self):
        self.__controller.set_servo_angle(self.__angle_on)

    def disable(self):
        self.__controller.set_servo_angle(self.__angle_off)
        