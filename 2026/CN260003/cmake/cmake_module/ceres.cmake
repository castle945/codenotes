# 添加依赖库 pcl
find_package(Ceres)
include_directories(${CERES_INCLUDE_DIRS})
list(APPEND ALL_TARGET_LIBRARIES ${CERES_LIBRARIES})
