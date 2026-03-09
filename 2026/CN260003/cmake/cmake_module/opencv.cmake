# opencv
set(OpenCV_DIR $ENV{HOME}/.local/lib/opencv-4.5.3/installed)
find_package(OpenCV)
include_directories(${OpenCV_INCLUDE_DIRS})
list(APPEND ALL_TARGET_LIBRARIES ${OpenCV_LIBS})  