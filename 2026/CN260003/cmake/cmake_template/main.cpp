// 持续发送 UDP 消息
#include "defination.h"
#include <yaml-cpp/yaml.h>

#include <udpclient.h>
#include <unistd.h>
#include <stdio.h>
#include <string>
#include <string.h>

using namespace utilscpp;

int main(int argc, char* argv[])
{
    // 配置文件与参数
    YAML::Node config_node;
    std::string config_file_path = WORK_SPACE_PATH + "/config/config.yaml";
    config_node = YAML::LoadFile(config_file_path);
    std::string ip = config_node["ip"].as<std::string>();
    int port = config_node["port"].as<int>();
    int interval = config_node["interval"].as<int>();
    std::string msg = config_node["msg"].as<std::string>();

    UdpClient udpClient;
    char buf[102400];
    int count = 0;

    udpClient.InitAsNormClient(ip.c_str(), port);
    while(1)
    {
        std::string cur_msg = msg + std::to_string(count++);
        sprintf(buf, cur_msg.c_str());
        udpClient.Send(buf, strlen(cur_msg.c_str()));
        printf("%s\n", buf);

        sleep(interval);
    }
    return 0;
}


