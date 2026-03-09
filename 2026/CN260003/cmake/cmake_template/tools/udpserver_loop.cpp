// 持续接收 UDP 消息
#include "defination.h"
#include <yaml-cpp/yaml.h>

#include <udpserver.h>
#include <unistd.h>
#include <stdio.h>
#include <string>
#include <string.h>

using namespace utilscpp;

int main(int argc, char const *argv[])
{
    // 配置文件与参数
    YAML::Node config_node;
    std::string config_file_path = WORK_SPACE_PATH + "/config/config.yaml";
    config_node = YAML::LoadFile(config_file_path);
    int port = config_node["port"].as<int>();

    UdpServer udpServer;
    char buf[102400];

    udpServer.Initialize(port);
    while(1)
    {
        memset(buf, 0, sizeof(buf));
        int nBytes = udpServer.Receive(buf, sizeof(buf));
        buf[nBytes+1] = '\0';
        // for(int i = 0; i < 12; i++) printf("%02x ", buf[i]);
        // printf("\n");
        printf("%s\n", buf);
    }   

}
