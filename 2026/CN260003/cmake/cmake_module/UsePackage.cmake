###############################################################################
# UsePackage: use FetchContent to make packages available
# 修改自 https://gitlab.com/mariokonrad/timesheet/-/blob/master/cmake/UsePackage.cmake
# 先将仓库拷贝在本地，只使用本地仓库
# Usage:
# include(UsePackage)
# use_git_package(
# 	TARGET googletest
# 	GIT_TAG release-1.11.0
# 	LOCAL "$ENV{HOME}/.cmake-local/git-repo/googletest"
# 	REMOTE "https://hub.fastgit.xyz/google/googletest.git"
# 	VARIABLES
# 		BUILD_GMOCK TRUE  BOOL
# 		BUILD_GTEST FALSE BOOL
# 	)
# 
# use_tar_package(
# 	TARGET googletest
# 	LOCAL "$ENV{HOME}/.cmake-local/tar-repo/googletest/release-1.11.0.tar.gz"
# 	REMOTE "https://hub.fastgit.xyz/google/googletest/archive/release-1.11.0.tar.gz"
# 	VARIABLES
# 		BUILD_GMOCK TRUE  BOOL
# 		BUILD_GTEST FALSE BOOL
# 	)
###############################################################################


function(use_git_package)
	include(CMakeParseArguments)
	cmake_parse_arguments(
		ARG
		"" # no values
		"TARGET;GIT_TAG;LOCAL;REMOTE" # single values
		"VARIABLES" # multi values
		${ARGN}
		)

	if(NOT DEFINED ARG_TARGET)
		message(FATAL_ERROR "use_git_pacakge: TARGET not specified")
	endif()

	if(NOT DEFINED ARG_GIT_TAG)
		message(FATAL_ERROR "use_git_pacakge: GIT_TAG not specified")
	endif()

	if(NOT DEFINED ARG_LOCAL)
		message(FATAL_ERROR "use_git_pacakge: LOCAL not specified")
	endif()

	if(NOT DEFINED ARG_REMOTE)
		message(FATAL_ERROR "use_git_pacakge: REMOTE not specified")
	endif()

	file(TO_CMAKE_PATH "${ARG_LOCAL}" path)
	if(NOT IS_DIRECTORY "${path}")
		execute_process(COMMAND git clone ${ARG_REMOTE} ${path})
	endif()
	set(target_repo "file://${path}")

	if(DEFINED ARG_VARIABLES)
		list(LENGTH ARG_VARIABLES len_total)
		if(${len_total} EQUAL 0)
			message(FATAL_ERROR "use_package: key/value/type tuples must be specified in VARIABLES")
		endif()
		math(EXPR len2 "${len_total} % 3")
		math(EXPR len  "${len_total} / 3 - 1")
		if(NOT len2 EQUAL 0)
			message(FATAL_ERROR "use_package: key/value/type tuples must be specified in VARIABLES")
		endif()
		foreach(index RANGE ${len})
			math(EXPR key_index "${index} * 3")
			math(EXPR val_index "${index} * 3 + 1")
			math(EXPR type_index "${index} * 3 + 2")
			list(GET ARG_VARIABLES ${key_index} key)
			list(GET ARG_VARIABLES ${val_index} val)
			list(GET ARG_VARIABLES ${type_index} type)
			set(${key} ${val} CACHE ${type} \"\" FORCE)
		endforeach()
	endif()

	message(STATUS "use_git_package: ${ARG_TARGET} from ${target_repo}")

	include(FetchContent)
	FetchContent_Declare(${ARG_TARGET}
		GIT_REPOSITORY "${target_repo}"
		GIT_TAG ${ARG_GIT_TAG}
		)
	FetchContent_MakeAvailable(${ARG_TARGET})
endfunction()


function(use_tar_package)
	include(CMakeParseArguments)
	cmake_parse_arguments(
		ARG
		"" # no values
		"TARGET;LOCAL;REMOTE" # single values
		"VARIABLES" # multi values
		${ARGN}
		)

	if(NOT DEFINED ARG_TARGET)
		message(FATAL_ERROR "use_tar_pacakge: TARGET not specified")
	endif()

	if(NOT DEFINED ARG_LOCAL)
		message(FATAL_ERROR "use_tar_pacakge: LOCAL not specified")
	endif()

	if(NOT DEFINED ARG_REMOTE)
		message(FATAL_ERROR "use_tar_pacakge: REMOTE not specified")
	endif()

	file(TO_CMAKE_PATH "${ARG_LOCAL}" path)
	if(NOT EXISTS "${path}")
		execute_process(COMMAND curl -o ${path} --create-dirs -L ${ARG_REMOTE})
	endif()
	set(target_repo "file://${path}")

	if(DEFINED ARG_VARIABLES)
		list(LENGTH ARG_VARIABLES len_total)
		if(${len_total} EQUAL 0)
			message(FATAL_ERROR "use_package: key/value/type tuples must be specified in VARIABLES")
		endif()
		math(EXPR len2 "${len_total} % 3")
		math(EXPR len  "${len_total} / 3 - 1")
		if(NOT len2 EQUAL 0)
			message(FATAL_ERROR "use_package: key/value/type tuples must be specified in VARIABLES")
		endif()
		foreach(index RANGE ${len})
			math(EXPR key_index "${index} * 3")
			math(EXPR val_index "${index} * 3 + 1")
			math(EXPR type_index "${index} * 3 + 2")
			list(GET ARG_VARIABLES ${key_index} key)
			list(GET ARG_VARIABLES ${val_index} val)
			list(GET ARG_VARIABLES ${type_index} type)
			set(${key} ${val} CACHE ${type} \"\" FORCE)
		endforeach()
	endif()

	message(STATUS "use_tar_package: ${ARG_TARGET} from ${target_repo}")

	include(FetchContent)
	FetchContent_Declare(${ARG_TARGET}
		QUIET
		URL "${target_repo}"
		)
	FetchContent_MakeAvailable(${ARG_TARGET})
endfunction()