# 声明要求的 cmake 最低版本
cmake_minimum_required(VERSION 3.0)
# 声明一个 cmake 工程
project(ros_test)
# 指定语言标准
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 编译选项
# SET(CMAKE_BUILD_TYPE "Release")
SET(CMAKE_BUILD_TYPE "RelWithDebInfo") # vscode ros 调试用
SET(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS} -O3 -Wall")
# 其他设置选项
# 设置cmake自定义模块脚本路径
# list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

# 添加依赖
set(ALL_TARGET_LIBRARIES "")
include(cmake/pcl.cmake)
include(cmake/glog.cmake)
include(cmake/yaml-cpp.cmake)

# catkin 依赖
find_package(catkin REQUIRED COMPONENTS
  ros_msgs # 自定义msg包必须放前面
  roscpp
  tf
  pcl_ros
  pcl_conversions
)
include_directories(${catkin_INCLUDE_DIRS})
link_directories(${catkin_LIBRARY_DIRS})
list(APPEND ALL_TARGET_LIBRARIES ${catkin_LIBRARIES})
catkin_package()

# 添加包含目录
include_directories(${PROJECT_SOURCE_DIR}/include)

file(GLOB_RECURSE ALL_SRCS "src/*.cpp")
file(GLOB_RECURSE NODE_SRCS "src/*_node.cpp")
list(REMOVE_ITEM ALL_SRCS ${NODE_SRCS})

add_executable(test_node src/test_node.cpp ${ALL_SRCS})
target_link_libraries(test_node ${ALL_TARGET_LIBRARIES})