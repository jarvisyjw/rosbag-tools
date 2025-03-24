"""A script to play raw image footage."""
import argparse
from rosbag import Bag
from tqdm import tqdm
from src.ros_utils import get_camera_image
from src.window import Window
from PIL import Image
import os.path as osp
import os


# def bag_to_images(bag: rosbag.Bag, output_path: str, topic: str, timestamp: str):
    
#     """
#     Convert a ROS bag with image topic to images with timestamp as names.
    
#     Args:
#             bag: the bag file to get image data from
#             output_file: the path to a directory to write images to
#             topic: the topic to read image data from
    
#     Returns:
#             None
    
#     """
    
#     # get the total number of frames to write
#     total_frames = bag.get_message_count(topic_filters=topic)
#     print(f"Total frames: {total_frames} in {topic}")

#     # get an iterator for the topic with the frame data
#     iterator = bag.read_messages(topics=topic)
#     # check if the output directory exists
#     if not os.path.isdir(output_path):
#             # create the output directory
#             os.makedirs(output_path)
    
#     # iterate over the image messages of the given topic
#     i = 0
#     f =  open(timestamp, 'w')
    
#     for _, msg, _ in tqdm(iterator, total=total_frames):
#             # basic info
#             encoding = msg.encoding
#             data = msg.data
#             width = msg.width
#             height = msg.height
#             timestamp = "%.6f" % msg.header.stamp.to_sec()
            
#             # read the image data into a NumPy tensor
#             np_arr = np.frombuffer(data, np.uint8).reshape((msg.height, msg.width, -1))
#             if np_arr.shape[2] == 1:
#                 np_arr = np_arr.reshape((height, width))
            
#             if encoding == 'rgb8':
#             # Convert from RGB to PIL image
#                 img = PILImage.fromarray(np_arr, 'RGB')
#             elif encoding == 'bgr8':
#                 # Convert from BGR to RGB then to PIL image
#                 np_arr = np_arr[..., ::-1]  # Reverse the last dimension (BGR -> RGB)
#                 img = PILImage.fromarray(np_arr, 'RGB')
#             else:
#                 # Handle other encodings if needed
#                 img = PILImage.fromarray(np_arr)
            
#             img_path = os.path.join(output_path, str(i) + '.png')
#             img.save(img_path)
#             f.write(timestamp + ' ' + str(i) + '.png' +'\n')
#             # Save the image
#             i += 1

#     f.close()
#     print(f"Total frames written: {i}")
#     print(f"Images written to {output_path} Done!")
    
#     return output_path, timestamp

def extract_images(bag_file: Bag, topics: list, output: str, format:str) -> None:
    """
    Play the data in a bag file.

    Args:
        bag_file: the bag file to play
        topics: the list of topics to play

    Returns:
        None

    """
    # create path
    if not osp.isdir(output):
        # create the output directory
        os.makedirs(output)
    # open windows to stream the camera and a priori image data to
    windows = {topic: None for topic in topics}
    # iterate over the messages
    progress = tqdm(total=bag_file.get_message_count(topic_filters=topics))
    
    if format == "tum":
        fout = open(osp.join(output, 'rgb.txt'), 'w')
        output_path = osp.join(output, 'rgb')
        if not osp.isdir(output_path):
            os.makedirs(output_path)
    else:
        raise NotImplementedError(f"{format} is not supported")
        
    for topic, msg, time in bag_file.read_messages(topics=topics):
        # if topic is camera, unwrap and send to the camera window
        if topic in topics:
            # update the progress bar with an iteration
            progress.update(1)
            # update the progress with a post fix
            progress.set_postfix(time=time)
            # if the camera window isn't open, open it5
            if windows[topic] is None:
                title = '{} ({})'.format(bag_file.filename, topic)
                windows[topic] = Window(title, msg.height, msg.width)
            # get the pixels of the camera image and display them
            img = get_camera_image(msg.data, windows[topic].shape)
            if msg.encoding == 'bgr8':
                img = img[..., ::-1]
            windows[topic].show(img[..., :3])
            # save the image
            img = Image.fromarray(img)
            if format == "tum":
                time = "%.6f" % time.to_sec()
                path = osp.join(output_path, f"{time}.png")
                str = f"{time} rgb/{time}.png\n"
                fout.write(str)
                img.save(path)
            else:
                raise NotImplementedError(f"{format} is not supported")


    # shut down the viewer windows
    for window in windows.values():
        if window is not None:
            window.close()


# ensure this script is running as the main entry point
if __name__ == '__main__':
    # create an argument parser to read arguments from the command line
    PARSER = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # add an argument for the bag file
    PARSER.add_argument('--bag_file', '-b',
        type=str,
        help='The bag file containing the ZED data to play.',
        required=True,
    )
    # add an argument for the camera topics
    PARSER.add_argument('--topics', '-t',
        type=str,
        nargs='+',
        help='The raw image topics to play.',
        required=True,
    )
    PARSER.add_argument('--output_dir', '-o',
        type=str,
        help='The directory to save the images to.',
        required=True,
    )
    PARSER.add_argument('--format', '-f',
        type=str,
        help='The format to save the images in.',
        default='tum',
    )
    try:
        # get the arguments from the argument parser
        ARGS = PARSER.parse_args()
        # open the bag file in a content manager
        with Bag(ARGS.bag_file, 'r') as BAG_FILE:
            # play the bag with the given camera topics
            extract_images(BAG_FILE, ARGS.topics, ARGS.output_dir, ARGS.format)
    except KeyboardInterrupt:
        pass


# explicitly define the outward facing API of this module
__all__ = [extract_images.__name__]
