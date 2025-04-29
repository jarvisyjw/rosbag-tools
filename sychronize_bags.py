import rosbag
from rospy import Time

def synchronize_bags(bag1_path, bag2_path, output_bag_path, topic1, topic2, time_tolerance=0.01):
    """
    Synchronize two ROS bags by matching timestamps of messages on specified topics.

    Args:
        bag1_path (str): Path to the first bag file.
        bag2_path (str): Path to the second bag file.
        output_bag_path (str): Path to save the synchronized bag.
        topic1 (str): Topic to synchronize from bag1.
        topic2 (str): Topic to synchronize from bag2.
        time_tolerance (float): Time difference tolerance in seconds.
    """
    bag1 = rosbag.Bag(bag1_path, 'r')
    bag2 = rosbag.Bag(bag2_path, 'r')
    output_bag = rosbag.Bag(output_bag_path, 'w')

    try:
        # Extract messages from both bags
        bag1_msgs = [(msg, t) for _, msg, t in bag1.read_messages(topics=[topic1])]
        bag2_msgs = [(msg, t) for _, msg, t in bag2.read_messages(topics=[topic2])]

        # Synchronize messages based on timestamps
        i, j = 0, 0
        while i < len(bag1_msgs) and j < len(bag2_msgs):
            msg1, time1 = bag1_msgs[i]
            msg2, time2 = bag2_msgs[j]

            time_diff = abs((time1 - time2).to_sec())
            if time_diff <= time_tolerance:
                # Write synchronized messages to the output bag
                output_bag.write(topic1, msg1, time1)
                output_bag.write(topic2, msg2, time2)
                i += 1
                j += 1
            elif time1 < time2:
                i += 1
            else:
                j += 1
    finally:
        bag1.close()
        bag2.close()
        output_bag.close()

if __name__ == '__main__':
    # Example usage
    synchronize_bags(
        bag1_path='data/FusionPortable_dataset_release/sensor_data/handheld/20220216_corridor_day/odom_fastlio.bag',
        bag2_path='data/FusionPortable_dataset_release/sensor_data/handheld/20220216_corridor_day/stereo_frame_left.bag',
        output_bag_path='stereo_frame_left_odom_fastlio_sync.bag',
        topic1='/Odometry',
        topic2='/stereo/frame_left/image_raw',
        time_tolerance=0.01  # 10 ms tolerance
    )