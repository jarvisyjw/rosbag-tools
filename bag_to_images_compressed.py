"""A script to play raw image footage."""
import argparse
from rosbag import Bag
from tqdm import tqdm
from src.ros_utils import get_camera_image_compressed
from src.window import Window
from PIL import Image
import os.path as osp
import os
import io
import numpy as np

def compressed_imgmsg_to_pil(compressed_img_msg):
    # Convert the compressed image data to a byte stream
    byte_stream = io.BytesIO(compressed_img_msg.data)
    # Open the image using PIL
    pil_image = Image.open(byte_stream)
    # Convert to RGB if needed
    pil_image = pil_image.convert('RGB')
    return pil_image

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
            try:
                img = compressed_imgmsg_to_pil(msg)
                if windows[topic] is None:
                    title = '{} ({})'.format(bag_file.filename, topic)
                    width, height = img.size
                    windows[topic] = Window(title, height, width)
            except Exception as e:
                print(f"Error converting image: {e}")
                continue
        
            windows[topic].show(np.array(img))
                            
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
