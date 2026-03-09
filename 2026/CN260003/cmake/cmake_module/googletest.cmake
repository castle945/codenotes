include(UsePackage)
use_tar_package(
	TARGET googletest
	LOCAL "$ENV{HOME}/.cmake-local/tar-repo/googletest/release-1.11.0.tar.gz"
	REMOTE "https://hub.fastgit.xyz/google/googletest/archive/release-1.11.0.tar.gz"
	VARIABLES
		BUILD_GMOCK TRUE  BOOL
		BUILD_GTEST FALSE BOOL
	)