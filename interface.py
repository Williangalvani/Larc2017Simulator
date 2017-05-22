import numpy as np
from vreptest import vrep
import time


class Gripper:
    """
    Represents the robot's gripper, responsible for moving it.
    """

    def __init__(self, client_id):
        self.client_id = client_id
        _, self.gripper_camera = vrep.simxGetObjectHandle(client_id, "gripper_cam",
                                                          vrep.simx_opmode_blocking)
        _, self.gripper_target = vrep.simxGetObjectHandle(client_id, "gripper_target",
                                                          vrep.simx_opmode_blocking)
        _, self.gripper_resting = vrep.simxGetObjectHandle(client_id, "gripper_resting_position",
                                                           vrep.simx_opmode_blocking)

    def move(self, coords, incremental=True):
        """
        Moves the gripper to (left, away, up)
        :param coords: position to move to(if not incremental) or to increase (if incremental)
        :param incremental: relative to actual position
        """
        if incremental:
            vrep.simxSetObjectPosition(self.client_id, self.gripper_target, self.gripper_target,
                                       coords, vrep.simx_opmode_oneshot)
        else:
            vrep.simxSetObjectPosition(self.client_id, self.gripper_target, self.gripper_resting,
                                       coords, vrep.simx_opmode_oneshot)


class RobotInterface:
    """
    This is responsible for interfacing with the simulated robot
    """

    def __init__(self):
        vrep.simxFinish(-1)  # just in case, close all opened connectionsS
        self.client_id = vrep.simxStart("127.0.0.1", 19997, True, True, 5000, 5)

        vrep.simxStopSimulation(self.client_id, vrep.simx_opmode_oneshot)
        vrep.simxStartSimulation(self.client_id, vrep.simx_opmode_oneshot)

        vrep.simxSynchronous(self.client_id, False)
        print("connected with id ", self.client_id)

        self.left_wheel = None
        self.right_wheel = None
        self.camera = None
        self.gripper = None

        self.setup()

    def finish_iteration(self):
        vrep.simxSynchronousTrigger(self.client_id)

    def set_right_speed(self, speed):
        """
        seta velocidade da roda direita
        :param speed:
        :return:
        """
        vrep.simxSetJointTargetVelocity(self.client_id, self.right_wheel, speed,
                                        vrep.simx_opmode_oneshot)

    def set_left_speed(self, speed):
        """
        seta velocidade da roda esquerda
        :param speed:
        :return:
        """
        vrep.simxSetJointTargetVelocity(self.client_id, self.left_wheel, speed,
                                        vrep.simx_opmode_oneshot)

    def _read_camera(self, handle):
        data = vrep.simxGetVisionSensorImage(self.client_id, handle, 1, vrep.simx_opmode_buffer)
        if data[0] == vrep.simx_return_ok:
            return data
        return None

    def get_image_from_camera(self, handle):
        """
        Loads image from camera.
        :return:
        """
        img = None
        while not img:
            img = self._read_camera(handle)
            time.sleep(0.001)
        size = img[1][0]
        img = np.flipud(np.array(img[2], dtype='uint8').reshape((size, size)))
        return img

    def get_position_from_handle(self, handle):
        """
        Return [position, orientation] of handle
        :param handle:
        :return:
        """
        pos = [[], []]
        _, pos[0] = vrep.simxGetObjectPosition(self.client_id, handle, - 1,
                                               vrep.simx_opmode_streaming)
        _, pos[1] = vrep.simxGetObjectOrientation(self.client_id, handle, - 1,
                                                  vrep.simx_opmode_streaming)
        return pos

    def stop(self):
        vrep.simxStopSimulation(self.client_id, vrep.simx_opmode_oneshot_wait)

    def setup(self):
        if self.client_id != -1:
            _, self.camera = vrep.simxGetObjectHandle(self.client_id, "Vision_sensor",
                                                      vrep.simx_opmode_blocking)
            _, self.left_wheel = vrep.simxGetObjectHandle(self.client_id, "fl_wheel_joint",
                                                          vrep.simx_opmode_blocking)
            _, self.right_wheel = vrep.simxGetObjectHandle(self.client_id, "fr_wheel_joint",
                                                           vrep.simx_opmode_blocking)
            vrep.simxGetVisionSensorImage(self.client_id, self.camera, 1,
                                          vrep.simx_opmode_streaming)
            self.gripper = Gripper(self.client_id)
