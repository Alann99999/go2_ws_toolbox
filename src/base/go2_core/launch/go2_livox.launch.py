import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # Livox MID-360 参数配置
    xfer_format = 0       # 0=PointCloud2(PointXYZRTL), 1=自定义格式
    multi_topic = 0       # 0=所有雷达共用同一话题, 1=每个雷达独立话题
    data_src = 0          # 0=雷达实时数据
    publish_freq = 10.0   # 发布频率 (Hz)
    output_type = 0
    frame_id = 'livox_frame'  # Livox 雷达自身坐标系
    lvx_file_path = '/home/livox/livox_test.lvx'
    cmdline_bd_code = 'livox0000000001'

    # 自定义 MID-360 配置文件路径
    cur_config_path = os.path.join(
        get_package_share_directory('go2_core'),
        'config',
        'MID360_config.json'
    )

    livox_ros2_params = [
        {"xfer_format": xfer_format},
        {"multi_topic": multi_topic},
        {"data_src": data_src},
        {"publish_freq": publish_freq},
        {"output_data_type": output_type},
        {"frame_id": frame_id},
        {"lvx_file_path": lvx_file_path},
        {"user_config_path": cur_config_path},
        {"cmdline_input_bd_code": cmdline_bd_code}
    ]

    # Livox MID-360 驱动节点
    # 将 /livox/lidar 话题重映射到 /utlidar/cloud_deskewed,
    # 以对接现有的 cloud_accumulation -> pointcloud_to_laserscan -> slam 管线
    livox_driver = Node(
        package='livox_ros_driver2',
        executable='livox_ros_driver2_node',
        name='livox_lidar_publisher',
        output='screen',
        parameters=livox_ros2_params,
        remappings=[
            ('/livox/lidar', '/utlidar/cloud_deskewed'),
        ]
    )

    # 静态坐标变换: base_link -> livox_frame
    # 将 Livox 雷达坐标系连接到机器人本体坐标系
    # 默认使用单位变换，可根据实际安装位置调整 x/y/z/roll/pitch/yaw
    static_tf_livox = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_base_link_to_livox',
        arguments=[
            '--x', '0.0',
            '--y', '0.0',
            '--z', '0.35',      # MID-360 安装高度 (相对 base_link)
            '--roll', '0.0',
            '--pitch', '0.0',
            '--yaw', '0.0',
            '--frame-id', 'base_link',
            '--child-frame-id', 'livox_frame'
        ],
        output='screen'
    )

    return LaunchDescription([
        livox_driver,
        static_tf_livox,
    ])
