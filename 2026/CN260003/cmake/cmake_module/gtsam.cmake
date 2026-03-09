# gtsam
set(GTSAM_DIR $ENV{HOME}/.local/lib/gtsam-4.1/installed/lib/cmake/GTSAM)
find_package(GTSAM)
include_directories(${GTSAM_INCLUDE_DIR})
list(APPEND ALL_TARGET_LIBRARIES ${GTSAM_LIBS})  