# ROS 示例代码

### ros1_template - ROS1 模板代码

### rclpy - ROS2 示例代码

#### demo0000 - 创建空项目并发布简单话题 [ [1](https://blog.csdn.net/Kevin_Xie86/article/details/125990850) ]

```bash
mkdir -p ros2_ws/src && cd ros2_ws/src
ros2 pkg create ros2demo --build-type ament_python --dependencies rclpy # 创建 Python 包

cd ros2demo && rm -rf test
wget https://github.com/ros2/examples/raw/humble/rclpy/topics/minimal_publisher/examples_rclpy_minimal_publisher/publisher_member_function.py -P ros2demo/

# setup.py
entry_points={
    'console_scripts': [
        'publisher_member_function = ros2demo.publisher_member_function:main',
    ],
},
.
├── package.xml
├── resource
│   └── ros2demo                      # 构建需要，空文件，用于定义包的资源路径，告诉 ament 构造工具将 resource 目录添加到资源搜索路径
├── ros2demo
│   ├── __init__.py
│   └── publisher_member_function.py
├── setup.cfg
├── setup.py
└── test

colcon build
source install/local_setup.zsh
ros2 run ros2demo publisher_member_function
ros2 topic echo /topic
```

#### demo0001 - VSCode 调试、发布点云并编写 launch 文件 [ [1](https://github.com/ms-iot/vscode-ros/issues/872) | [1](https://github.com/HaiderAbasi/ROS2-Path-Planning-and-Maze-Solving/blob/master/path_planning_ws/src/maze_bot/maze_bot/maze_solver.py)* [2](https://github.com/ros2/examples/blob/rolling/rclpy/topics/pointcloud_publisher/examples_rclpy_pointcloud_publisher/pointcloud_publisher.py) | [1](https://blog.csdn.net/qq_36372352/article/details/135402532) [2](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Using-Parameters-In-A-Class-Python.html) [3](https://roboticsbackend.com/rclpy-params-tutorial-get-set-ros2-params-with-python/)* ]

```bash
rviz2 -d src/ros2demo/rviz/demo.rviz
ros2 run ros2demo cloud_play_node
ros2 run ros2demo teleop_key_node

# or 
ros2 launch ros2demo demo.launch.py data_root:=/path/to/.bin/dir
ros2 run ros2demo teleop_key_node

# VSCode 调试 launch 文件
# 安装微软官方的 ROS 插件，打开项目后选择合适的 Python 解释器如 /usr/bin/python3
# 主侧边栏三角形调试按钮中点击显示所有自动调试配置，创建 ROS: Launch 调试(提前 colcon build 否则选不到 ros2demo 包)
# 此时会在 .vscode 下生成配置文件（没生成可以多试几次或者手动添加配置），修改 target 字段为 install 目录下的 lauch 文件的路径，启动调试
# 注意！！！断点应该打在 install 目录下的源码文件上，而不是 src 下的源码文件，位置例如 install/ros2demo/lib/python3.10/site-packages/ros2demo/cloud_play_node.py

# VSCode 调试节点
# launch 文件手动添加调试当前 python 文件的配置，点开要调试的节点文件，启动调试
# 注意！！！此时的断点打当前打开的文件中（这个打开的文件可以是 src 源码中的文件），不过该文件调用的文件还是 install 下打包的库代码中的文件
```

#### demo0002 - rqt_reconfigure 可视化调参与参数使用 [ [1](https://blog.csdn.net/2203_76027118/article/details/136740657)* ]

```bash
# 参考链接中的 C++ 代码修改
# ROS2 中不论动静态参数都可以直接 declare_parameter
# ros2 run ros2demo dynamic_param_node
ros2 run ros2demo dynamic_param_node --ros-args --params-file src/ros2demo/config/demo_param.yaml
ros2 run rqt_reconfigure rqt_reconfigure

ros2 launch ros2demo demo.launch.py
ros2 run ros2demo teleop_key_node
```
