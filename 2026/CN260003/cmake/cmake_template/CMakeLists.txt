# 声明要求的 cmake 最低版本
cmake_minimum_required(VERSION 3.0)
# 声明一个 cmake 工程
project(cmake_template)
# 指定语言标准
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 编译选项
# SET(CMAKE_BUILD_TYPE "Release")
# 其他设置选项
# 设置 cmake 自定义模块脚本路径
list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

# 添加依赖
set(ALL_TARGET_LIBRARIES "")
include(cmake/defination.cmake)
include(cmake/yaml-cpp.cmake)

# 添加头文件目录
include_directories(${PROJECT_SOURCE_DIR}/include)

# 编译可执行文件
file(GLOB_RECURSE ALL_SRCS "src/*.cpp")

add_executable(main main.cpp ${ALL_SRCS})
target_link_libraries(main ${ALL_TARGET_LIBRARIES})

add_executable(udpserver_loop tools/udpserver_loop.cpp ${ALL_SRCS})
target_link_libraries(udpserver_loop ${ALL_TARGET_LIBRARIES})
