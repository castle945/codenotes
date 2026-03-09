// g++ 示例程序

// @# demo0001-编译单个源文件: g++ -o main main.cpp # 无其他参数，此时与 make main 等价
// #include <iostream>
// int main(int argc, char* argv[]) {
//     std::cout << "demo0001" << std::endl;

//     return 0;
// }

// @# demo0002-编译带头文件的单个源文件: g++ -o main main.cpp -I./include
// #include <iostream>
// // #include "include/demo0002.h" // 如指定路径则不需要加 -I
// #include "demo0002.h"            // 否则需要编译时 -I 指定头文件路径
// int main(int argc, char* argv[]) {
//     std::cout << STR << std::endl;

//     return 0;
// }

// @# demo0003-编译调用系统库的多个源文件: g++ -o main main.cpp demo0003.cpp -I./include -lglog
// 系统库头文件存放于 /usr/include 或 /usr/local/include 中，库文件存放于 /usr/lib 或 /usr/local/lib 下，这些路径在搜索路径中，只需要给出链接的库名即可
// #include <iostream>
// #include "demo0002.h"            // 否则需要编译时 -I 指定头文件路径
// #include "demo0003.h"            // apt install -y libgoogle-glog-dev 库文件位于 /usr/lib/x86_64-linux-gnu/
// int main(int argc, char* argv[]) {
//     GLOG_INIT(argv[0]);
//     GLOG_INFO(STR);

//     return 0;
// }

// @# demo0004-编译调用第三方库的源文件: 先编译 demo0003.cpp 并打包静态链接库，-L 指定库文件目录 -l 指定链接的库名如果自定义库包含其他依赖库还需要带上其他依赖库名
// g++ -c demo0003.cpp -o demo0003.o -I./include && mkdir lib && ar rcs ./lib/libdemo.a demo0003.o && rm -f demo0003.o \
// g++ -o main main.cpp -I./include -L./lib -ldemo -lglog
#include <iostream>
#include "demo0002.h"
#include "demo0003.h"            // apt install -y libgoogle-glog-dev 库文件位于 /usr/lib/x86_64-linux-gnu/
int main(int argc, char* argv[]) {
    GLOG_INIT(argv[0]);
    GLOG_INFO(STR);

    return 0;
}
