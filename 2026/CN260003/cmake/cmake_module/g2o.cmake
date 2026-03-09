# g2o
list(APPEND CMAKE_MODULE_PATH $ENV{HOME}/.local/lib/g2o-202012/cmake_modules)
set(G2O_ROOT $ENV{HOME}/.local/lib/g2o-202012/installed)
find_package(G2O REQUIRED)
include_directories(${G2O_INCLUDE_DIR})
link_directories(${G2O_ROOT}/lib)
list(APPEND ALL_TARGET_LIBRARIES 
      ${G2O_TYPES_DATA}
      ${G2O_CORE_LIBRARY}
      ${G2O_STUFF_LIBRARY}
      ${G2O_SOLVER_PCG}
      ${G2O_SOLVER_CSPARSE}
      ${G2O_SOLVER_CHOLMOD}
      ${G2O_TYPES_SLAM3D}
      ${G2O_TYPES_ICP}
      ${G2O_TYPES_SBA}
      )
