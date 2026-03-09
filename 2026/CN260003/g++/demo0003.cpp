#include "demo0003.h"
#include <glog/logging.h>        // 包含 glog 的头文件

void GLOG_INIT(const char* argv0)
{
    // 初始化 glog 库，传入程序名作为日志标识
    google::InitGoogleLogging(argv0);
    // 设置日志目录（可选，默认会输出到 /tmp/）
    FLAGS_log_dir = "./";  // 日志文件将保存在当前目录下
}
void GLOG_INFO(std::string str)
{
    // 设置日志级别（可选）
    FLAGS_minloglevel = 0;  // 0: INFO, 1: WARNING, 2: ERROR, 3: FATAL
    // 记录不同级别的日志
    LOG(INFO) << str;
}