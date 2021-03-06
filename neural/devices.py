from tensorflow.python.client import device_lib
import tensorflow as tf

def get_available_gpus():
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos if x.device_type == 'GPU' or x.device_type == 'CPU']

if __name__ == '__main__':
    print('\n All devices:',get_available_gpus())