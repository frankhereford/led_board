import sys

sys.path.insert(1, "../radio/lib")
import layout as layout_library
import cv2
import numpy as np
import json
import time


def transform_coordinate(point, target_x_max=100, target_y_max=100):
    x, y = point

    # Transform X
    # Shift the X value from the range [-1, 1] to [0, 2] and then scale to [0, target_x_max]
    x_transformed = (x + 1) * (target_x_max / 2)

    # Transform Y
    # Scale the Y value from the range [0, 1] to [0, target_y_max]
    y_transformed = y * target_y_max

    return (int(x_transformed), int(y_transformed))


def precompute_light_positions(layout, width, height):
    light_positions = {}
    for ip in layout:
        #if ip not in ("10.10.10.154", "10.10.10.155"):
            #continue
        for group in layout[ip]:
            for index, light in enumerate(layout[ip][group]):
                # Calculate the transformed coordinate
                transformed_point = transform_coordinate(
                    (light["coordinate"]["x"], light["coordinate"]["y"]),
                    width - 1,
                    height - 1,
                )

                # Ensure the coordinate is a key in the dictionary
                if transformed_point not in light_positions:
                    light_positions[transformed_point] = []

                # Append the light identifier to the list for this coordinate
                light_positions[transformed_point].append((ip, group, index))

    return light_positions


def resize_with_border_shift(original_frame, scale_factor, shift_x, shift_y):
    # Resize the frame according to the scale factor
    small_frame = cv2.resize(original_frame, (0, 0), fx=scale_factor, fy=scale_factor)

    # Create a black image with the same dimensions as the original frame
    border_frame = np.zeros_like(original_frame)

    # Calculate the starting points to place the small frame, including the shifts
    start_x = max((border_frame.shape[1] - small_frame.shape[1]) // 2 + shift_x, 0)
    start_y = max((border_frame.shape[0] - small_frame.shape[0]) // 2 + shift_y, 0)

    # Ensure the small frame is fully within the border_frame dimensions
    end_x = min(start_x + small_frame.shape[1], border_frame.shape[1])
    end_y = min(start_y + small_frame.shape[0], border_frame.shape[0])

    # Adjust small_frame if necessary to fit into border_frame
    adjusted_small_frame = small_frame[: end_y - start_y, : end_x - start_x]

    # Place the adjusted small frame in the border_frame
    border_frame[start_y:end_y, start_x:end_x] = adjusted_small_frame

    return border_frame


while True:
    # Load the video
    video_path = "mario.mp4"
    cap = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print("Error opening video file")

    # Get the resolution of the video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Video resolution: {width}x{height}")

    layout = layout_library.read_json_from_file("installation_v2_groups.json")
    light_positions = precompute_light_positions(layout, width, height)

    # Initialize a frame counter
    frame_number = 0

    # Iterate over each frame
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            #frame = frame_with_border_shift = resize_with_border_shift(frame, 0.30, 78, 60)
            # Get the dimensions of the frame
            height, width, _ = frame.shape

            for (x, y), lights in light_positions.items():
                # Invert the y-coordinate to correct the upside-down issue
                inverted_y = (
                    height - y - 1
                )  # Subtracting 1 because coordinates are 0-indexed

                color_sample = frame[inverted_y, x, :]
                # print(f"Frame {frame_number}, pixel ({x}, {y}): {color_sample}")

                for ip, group, index in lights:
                    # print(color_sample[0])
                    layout[ip][group][index]["color"] = {
                        "r": int(color_sample[2]),
                        "g": int(color_sample[1]),
                        "b": int(color_sample[0]),
                    }

            layout_library.replace_value_atomic(
                "installation_layout", json.dumps(layout)
            )

            # Increment the frame counter
            frame_number += 1
            time.sleep(0.02)

        else:
            break

    # When everything done, release the video capture object
    cap.release()
    cv2.destroyAllWindows()
