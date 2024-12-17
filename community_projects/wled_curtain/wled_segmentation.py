import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import sys
import numpy as np
import cv2
import hailo
sys.path.append('../../basic_pipelines')

from hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
from instance_segmentation_pipeline import GStreamerInstanceSegmentationApp

from wled_display import WLEDDisplay

# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.wled = WLEDDisplay(panels=3, udp_enabled=True)


# Predefined colors (BGR format)
COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Cyan
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Yellow
    (128, 0, 128),  # Purple
    (255, 165, 0),  # Orange
    (0, 128, 128),  # Teal
    (128, 128, 0)   # Olive
]

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------

# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    # Check if the buffer is valid
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # Using the user_data to count the number of frames
    user_data.increment()
    string_to_print = f"Frame count: {user_data.get_count()}\n"

    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Reduce the resolution by a factor of 2
    reduced_width = width // 2
    reduced_height = height // 2
    reduced_frame = cv2.resize(frame, (reduced_width, reduced_height), interpolation=cv2.INTER_LINEAR)

    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Parse the detections
    for detection in detections:
        label = detection.get_label()
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()
        if label == "person":
            string_to_print += (f"Detection: {label} {confidence:.2f}\n")
            # Get track ID
            track_id = 0
            track = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
            if len(track) == 1:
                track_id = track[0].get_id()

            # Instance segmentation mask from detection (if available)
            masks = detection.get_objects_typed(hailo.HAILO_CONF_CLASS_MASK)
            if len(masks) != 0:
                mask = masks[0]
                # Note that the mask is a 1D array, you need to reshape it to get the original shape
                mask_height = mask.get_height()
                mask_width = mask.get_width()
                data = np.array(mask.get_data())
                data = data.reshape((mask_height, mask_width))
                # Resize the mask to the ROI size
                roi_width = int(bbox.width() * reduced_width)
                roi_height = int(bbox.height() * reduced_height)
                resized_mask_data = cv2.resize(data, (roi_width, roi_height), interpolation=cv2.INTER_LINEAR)

                # Calculate the ROI coordinates
                x_min, y_min = int(bbox.xmin() * reduced_width), int(bbox.ymin() * reduced_height)
                x_max, y_max = x_min + roi_width, y_min + roi_height

                # Ensure the ROI dimensions match the resized mask dimensions
                if y_max > reduced_frame.shape[0]:
                    y_max = reduced_frame.shape[0]
                if x_max > reduced_frame.shape[1]:
                    x_max = reduced_frame.shape[1]

                # Add mask overlay to the frame
                mask_overlay = np.zeros_like(reduced_frame)
                color = COLORS[track_id % len(COLORS)]  # Get color based on track_id
                mask_overlay[y_min:y_max, x_min:x_max] = np.dstack([(resized_mask_data[:y_max-y_min, :x_max-x_min] > 0.5) * c for c in color])
                reduced_frame = cv2.addWeighted(reduced_frame, 1, mask_overlay, 0.5, 0)

    # Resize the frame back to the original size for display
    frame = cv2.resize(reduced_frame, (width, height), interpolation=cv2.INTER_LINEAR)
    frame = cv2.resize(frame, (user_data.wled.panel_width * user_data.wled.panels, user_data.wled.panel_height))
    user_data.wled.frame_queue.put(frame)

    print(string_to_print)
    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    app = GStreamerInstanceSegmentationApp(app_callback, user_data)
    app.run()
