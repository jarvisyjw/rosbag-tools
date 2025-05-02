# Using this file as follows:
# python bag_to_vslam.py \
#   --bag_file data/my_record.bag \
#   --topic /camera/image/compressed \
#   --output_dir ./vslam_dataset/ \
#   --sequence_name sequence_01

import argparse
import os
import os.path as osp
import io
from rosbag import Bag
from PIL import Image
from tqdm import tqdm


def compressed_imgmsg_to_pil(compressed_img_msg):
    byte_stream = io.BytesIO(compressed_img_msg.data)
    pil_image = Image.open(byte_stream)
    return pil_image.convert('RGB')

def extract_images_for_vslamlab(bag_file: Bag, topic: str, output_dir: str, sequence_name: str):
    sequence_dir = osp.join(output_dir, sequence_name)
    rgb_dir = osp.join(sequence_dir, 'rgb')
    os.makedirs(rgb_dir, exist_ok=True)

    rgb_txt_path = osp.join(sequence_dir, 'rgb.txt')
    rgb_txt = open(rgb_txt_path, 'w')

    messages = list(bag_file.read_messages(topics=[topic]))
    progress = tqdm(total=len(messages), desc='Extracting images')

    for idx, (topic, msg, time) in enumerate(messages):
        try:
            img = compressed_imgmsg_to_pil(msg)
        except Exception as e:
            print(f"[Warning] Failed to decode image at {time}: {e}")
            continue

        timestamp = "%.6f" % time.to_sec()
        filename = f"img_{idx:04d}.png"
        img_path = osp.join(rgb_dir, filename)
        img.save(img_path)

        rgb_txt.write(f"{timestamp} {filename}\n")
        progress.update(1)

    rgb_txt.close()
    print(f"[Done] Saved {idx+1} images and rgb.txt to {sequence_dir}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert ROS .bag to VSLAM-LAB dataset format")
    parser.add_argument('--bag_file', '-b', type=str, required=True, help="Path to .bag file")
    parser.add_argument('--topic', '-t', type=str, required=True, help="Image topic (e.g. /camera/image/compressed)")
    parser.add_argument('--output_dir', '-o', type=str, required=True, help="Output directory for VSLAM-LAB format")
    parser.add_argument('--sequence_name', '-s', type=str, default='sequence_01', help="Name of the output sequence folder")
    args = parser.parse_args()

    with Bag(args.bag_file, 'r') as bag:
        extract_images_for_vslamlab(bag, args.topic, args.output_dir, args.sequence_name)
