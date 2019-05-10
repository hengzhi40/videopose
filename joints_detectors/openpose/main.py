import sys
import cv2
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path)

import argparse
from tqdm import tqdm
from utils import convert
import numpy as np

sys.path.remove(dir_path)

try:
    from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e

# Flags
parser = argparse.ArgumentParser()
parser.add_argument("--image_path", default="../../examples/media/COCO_val2014_000000000192.jpg", help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
args = parser.parse_known_args()

params = dict()
cur_dir = os.path.dirname(os.path.abspath(__file__))
params["model_folder"] = cur_dir + "/models/"
#  import ipdb;ipdb.set_trace()


def load_model():

    try:
        opWrapper = op.WrapperPython()
        opWrapper.configure(params)
        opWrapper.start()
    except Exception as e:
        print(e)
        sys.exit(-1)

    return opWrapper

def test_video(model, video_name=0):
    opWrapper = model

    cam = cv2.VideoCapture(video_name)
    # warm up
    for i in range(5):
        datum = op.Datum()
        _, imageToProcess = cam.read()
        datum.cvInputData = imageToProcess
        opWrapper.emplaceAndPop([datum])

    for i in tqdm(range(2000)):
        datum = op.Datum()
        _, imageToProcess = cam.read()
        datum.cvInputData = imageToProcess
        opWrapper.emplaceAndPop([datum])

    # Display Image
    #  print("Body keypoints: \n" + str(datum.poseKeypoints))
    #  cv2.imshow("OpenPose 1.4.0 - Tutorial Python API", datum.cvOutputData)
    #  cv2.waitKey(10)
    #  cv2.destroyAllWindows()

def generate_kpts(video_name):
    kpt_results = []

    cap = cv2.VideoCapture(video_name)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    opWrapper = load_model()
    for i in tqdm(range(length)):

        try:
            datum = op.Datum()
            _, imageToProcess = cap.read()
            datum.cvInputData = imageToProcess
            opWrapper.emplaceAndPop([datum])
            results = datum.poseKeypoints

            #25 to 17
            assert len(results) == 1, 'videopose3D only support one pserson restruction'
            kpts = convert(results[0])
            kpt_results.append(kpts)
        except Exception as e:
            print(e)

    # pose processes
    result = np.array(kpt_results)
    return result


if __name__ == "__main__":
    generate_kpts(os.environ.get('VIDEO_PATH') + 'dance.mp4')
