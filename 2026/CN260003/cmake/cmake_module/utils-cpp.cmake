# utils-cpp
find_library(UTILS_CPP
    NAMES utils_cpp
    HINTS /usr/local/lib
)
list(APPEND ALL_TARGET_LIBRARIES ${UTILS_CPP})

# old version
# foreach(module base sock)
# find_library(UTILS_CPP_${module}
    # NAMES utils_${module}
    # HINTS /usr/local/lib
# )
# list(APPEND ALL_TARGET_LIBRARIES ${UTILS_CPP_${module}})
# endforeach()