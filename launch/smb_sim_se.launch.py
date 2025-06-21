from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource, FrontendLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PythonExpression
from ament_index_python.packages import get_package_share_directory
import os



def generate_launch_description():
    # Include the main gazebo launch file
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("smb_gazebo"),
                "launch",
                "gazebo.launch.py"
            ])
        )
    )
    
    static_tf_map_to_odom = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_map_to_odom",
        arguments=["0", "0", "0", "0", "0", "0", "map", "odom"],
        output="log",
    )

    # Kinematics controller node
    kinematics_controller = Node(
        package="smb_kinematics",
        executable="smb_kinematics_node",
        name="smb_kinematics_node",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    # Low-level gazebo controller node
    low_level_controller = Node(
        package="smb_low_level_controller_gazebo",
        executable="smb_low_level_controller_gazebo_node",
        name="smb_low_level_controller_gazebo_node",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )
    
    joy_to_cmd_vel = Node(
        package="smb_kinematics",
        executable="smb_cmd_vel",
        name="smb_cmd_vel",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )
    
    joy = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        output="log",
        parameters=[{"use_sim_time": True}],
    )

    # Terrain analysis node
    terrain_analysis = Node(
        package="terrain_analysis",
        executable="terrainAnalysis",
        name="terrainAnalysis",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    # Terrain analysis ext node
    terrain_analysis_ext = Node(
        package="terrain_analysis_ext",
        executable="terrainAnalysisExt",
        name="terrainAnalysisExt",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    # teleop_twist_joy launch include
    teleop_twist_joy_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("teleop_twist_joy"),
                "launch",
                "teleop-launch.py"
            ])
        ]),
        launch_arguments={"publish_stamped_twist": "true"}.items(),
        # output="log",
    )

    # dlio launch include
    dlio_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("direct_lidar_inertial_odometry"),
                "launch",
                "dlio.launch.py"
            ])
        ]),
        launch_arguments={
            "rviz": "false",
            "pointcloud_topic": "/rslidar/points",
            "imu_topic": "/imu/data_raw"
        }.items(),
        # output="log",
    )
    
    local_odometry = Node(
        package="smb_kinematics",
        executable="smb_global_to_local_odometry",
        name="smb_global_to_local_odometry",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )
    
    far_planner_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("far_planner"),
                "launch",
                "far_planner.launch"
            ])
        ]),
    )
    
    local_planner_launch = IncludeLaunchDescription(
        FrontendLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("local_planner"),
                "launch",
                "local_planner.launch"
            ])
        ]),
    )
    
    twist_pid = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("twist_pid_controller"),
                "launch",
                "twist_pid_controller.launch.py"
            ])
        ),
    )

    gmsf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("smb_estimator_graph_ros2"),
                "launch",
                "smb_estimator_graph_sim.launch.py"
            ])
        ),
    )

    open3d_slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("open3d_slam_ros"),
                "launch",
                "summer_school_slam_robot_launch.py"
            ])
        ),
        launch_arguments={
            "use_sim_time": "true"
        }.items(),
    )
    
    
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='far_rviz',
        arguments=[
            '-d',
            PathJoinSubstitution([
                get_package_share_directory('smb_bringup'),
                'rviz',
                'debug.rviz'
            ])
        ],
        respawn=False,
    )

    smb_ui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("smb_ui"),
                "launch",
                "smb_ui_sim.launch.py"
            ])
        ),
    )

    default_config_topics = os.path.join(get_package_share_directory('smb_bringup'), 'config', 'twist_mux_topics.yaml')
    
    config_topics = DeclareLaunchArgument(
            'config_topics',
            default_value=default_config_topics,
            description='Default topics config file'
    )

    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        output='screen',
        remappings={('/cmd_vel_out', '/cmd_vel')},
        parameters=[
            {'use_sim_time': True},
            LaunchConfiguration('config_topics')]
    )
    
    return LaunchDescription([
        # gazebo_launch,
        kinematics_controller,
        low_level_controller,
        # joy_to_cmd_vel,
        joy,
        # terrain_analysis,
        # terrain_analysis_ext,
        # teleop_twist_joy_launch,
        # dlio_launch,
        # local_odometry,
        # static_tf_map_to_odom,
        # far_planner_launch,
        # local_planner_launch,
        # twist_pid,
        config_topics,
        twist_mux,
        # rviz2,
        gmsf_launch,
        open3d_slam_launch,
        smb_ui
    ])