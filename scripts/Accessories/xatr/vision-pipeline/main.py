from __future__ import annotations
import mats               # PyMATS import – assumes XATR_ROOT is set
import sigma.service

# THE ABOVE IMPORTS MUST BE FIRST

import cv2
import time
import queue
import threading

import commons.utils_lib as utils
import commons.thread_lib2 as tlib2
import commons.simple_zmq_lib as zlib

from app.config import load_config

from app.sink.base import DetectionSink
from app.sink.mock_sink import MockSink
from app.sink.framework_sink import FrameworkSink
from app.sink.atak_sink import AtakSink

from app.sources.rtsp import RTSPSource
from app.sources.webcam import WebcamSource
from app.sources.video_file import VideoFileSource

class SinkPushQueue:
    """ handles the queue-ing and pushing of messages to Sink """
    def __init__(self, sink: DetectionSink):
        self.sink = sink

        self.message_queue = queue.SimpleQueue() # SimpleQueue.put() will never block
        tlib2.threadForeverNoWait(func=self.publishMessage)
    
    def push(self, gps_data, detection):
        self.message_queue.put(self.sink.create_msg(gps_data, detection))
    
    def publishMessage(self):
        while True:
            msg = self.message_queue.get()
            self.sink.publish(msg)

class DataRecorder:
    """ 
    Saves gps data and video frames to disk.
    savedir should be a volume-mounted folder specified in docker-compose.yml
    """
    def __init__(self, savedir:str):
        # avoids extra load time if we're not using the DataRecorder
        import skvideo.io

        # open up a file for the gps data and frame timestamps
        self.gps_filename = savedir + "/gps_data.txt"
        self.gps_file = open(self.gps_filename, 'w')

        self.frames_filename = savedir + "/frame_timestamps.txt"
        self.frames_file = open(self.frames_filename, 'w')

        # open up a video file to write frames to
        self.video_filename = savedir + "/video.mkv"
        self.video_output_params = {
            '-vcodec': 'ffv1',      # codec
        }
        self.video_writer = skvideo.io.FFmpegWriter(self.video_filename, outputdict=self.video_output_params)
    
    def save(self, gps_data, frame, frame_ts):
        """ saves gps data and video frame with timestamps """
        # save the gps data
        # gps_data_str = "-----------\n"
        gps_data_str = ""
        for key in gps_data:
            gps_data_str += str(key) + ","
            gps_data_str += str(gps_data[key][0]) + ","
            gps_data_str += str(gps_data[key][1]) + "\n"
        self.gps_file.write(gps_data_str)

        # save the frame timestamp
        self.frames_file.write(str(frame_ts) + "\n")

        # save the video frame
        self.video_writer.writeFrame(frame) # this will be color swapped, but avoids extra processing

        # flush buffer to disk
        self.gps_file.flush()
        self.frames_file.flush()


class DroneState:
    def __init__(self):
        """ 
        Stores all of the info in a central construct with thread protection
        """
        # thread lock
        self.lock = threading.Lock()

        # store data in dict for easy copy
        self.data = {}
    
    def getData(self):
        """ returns all the info as a dictionary copy """
        with self.lock:
            return self.data.copy()

    def processStateMessage(self, msg:dict):
        """ unpackes custom ZMQ message and updates drone state """
        msg_data = msg["data"]

        with self.lock:
            self.data.update(msg_data)


def build_source(config: dict):
    """ sets up a video source """
    source_cfg = config["source"]
    source_type = source_cfg["type"]

    if source_type == "webcam":
        return WebcamSource(device_index=int(source_cfg.get("value", 0)))
    if source_type == "video_file":
        return VideoFileSource(path=str(source_cfg["value"]))
    if source_type == "rtsp":
        return RTSPSource(url=str(source_cfg["value"]))

    raise ValueError(f"Unsupported source type: {source_type}")


def build_sink(config: dict):
    """ sets up a detection sink """
    sink_type = config.get("sink", {}).get("type")

    if sink_type == "mock":
        return MockSink()
    if sink_type == "framework":
        return FrameworkSink()
    if sink_type == "atak":
        # TODO: should these be params in config or env var?
        atak_ip_address = utils.getEnv("ATAK_IP_ADDRESS")
        atak_port_number = utils.getEnv("ATAK_PORT", cast=int)
        return AtakSink(atak_ip_address, atak_port_number)

    # XATR sink ------------------
    if sink_type == "xatr":
        # Optional: point to a specific ATR configuration file
        # e.g. config["sink"].get("cfg_path", None)
        cfg_path = config.get("sink", {}).get("cfg_path")
        from app.sink.xatr_sink import XatrSink
        return XatrSink(cfg_path=cfg_path)

    raise ValueError(f"Unsupported sink type: {sink_type}")

def build_detection_dicts(contacts, names: list[str]) -> list[dict]:
    """ formats detections according to sigma """
    detection_dicts = []
    for contact in contacts:
        # TODO: add back in try/except with narrow exception catch once we know what it is
        label = sigma.service._con_name(contact, names) if contact.type >= 0 else "UNKNOWN"
        detection_dict = {
            "label": label,
            "class_id": contact.type,
            "confidence": contact.classconf,
            "bbox_xyxy": sigma.service._bbox(contact),
        }

        detection_dicts.append(detection_dict)
    return detection_dicts


if __name__ == "__main__":
    # pull environment variables
    zmq_port = utils.getEnv("STATUS_PORT")

    atr_cfg_path = utils.getEnv("XATR_CONFIG")
    atr_cfg_names = utils.getEnv("XATR_CONFIG_NAMES")
    yaml_config_path = utils.getEnv("APP_CONFIG")

    save_playback_data_flag = utils.getEnv("RECORDING_ON", default=False)
    recorder = None
    if save_playback_data_flag:
        recording_dir = utils.getEnv("RECORDING_FOLDER")
        recorder = DataRecorder(recording_dir)


    # load in the ATR and sigma packages
    mats.pkg.scan()
    stm = mats.pkg.create("XatrImagePipeline")

    # load in the XATR config
    atr_cfg = mats.AtrConfig()
    atr_cfg.load(atr_cfg_path)
    stm.configure(atr_cfg)

    # load in the name file
    with open(atr_cfg_names, 'r') as f:
        names = [line.strip() for line in f.readlines() if line.strip()]

    # pull in vars from the yaml file
    config = load_config(yaml_config_path) # returns a yaml object from "import yaml"
    source_id = str(config["source"].get("source_id")) # a unique tag that gets attached to detections

    # print out config setup
    print("Starting pipeline...")
    print(f"Source: {config['source']['type']}")
    print(f"Source: {config['source']['value']}")
    print(f"Sink: {config.get('sink', {}).get('type')}")  

    # construct the video source and the stream sink
    source = build_source(config)
    sink = build_sink(config)

    # set up the ZMQ status subscriber
    state = DroneState()
    subscriber = zlib.SimpleZMQSubscriber(ip_address="127.0.0.1", port=zmq_port, callback=state.processStateMessage)

    # set up the Sink message publisher
    sink_publisher = SinkPushQueue(sink=sink)
 
    # start the video source
    source.open()

    # wait for gps
    print("Waiting for GPS...")
    while True:
        gps_data = state.getData()
        if len(gps_data) != 0:
            break
        time.sleep(1.0)
    print("Got GPS")

    # main event loop
    frame_counter = 0
    while True:
        # pull frame # shouldn't need a busy loop for current gstreamer setup
        ret, frame = source.read()
        if ret:
            # establish timestamp
            now = time.time()

            # pull the latest gps data
            # we can calculate data-lag/offset from here if desired
            gps_data = state.getData() # {key: [timestamp, data]}

            # run inference
            # input = sigma.service.image2input(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # contacts, _ = stm.process(input)
            # detection_dicts = build_detection_dicts(contacts, names)

            # for detection in detection_dicts:
            #     print(f"Queueing detection {detection['label']} to TAK")
            #     sink_publisher.push(gps_data, detection)

            # save to playback directory if the flag is set
            if save_playback_data_flag:
                recorder.save(gps_data, frame, now)

            # print and increment the frame counter
            frame_counter += 1
            print("Frame Count:", frame_counter)



