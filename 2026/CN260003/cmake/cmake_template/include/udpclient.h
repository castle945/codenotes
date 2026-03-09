///////////////////////////////////////////////////////////////////////////////
///
/// @copyright Copyright (C), 2021, 南京理工大学计算机科学与工程学院, 智能科学与技术系
/// @file      udpclient.h
/// @author    谢城
/// @date      2021-09-27
/// @brief     Udp做客户端的封装
///          
///////////////////////////////////////////////////////////////////////////////
#pragma once

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdint.h>

namespace utilscpp {

/**
 * Udp客户端类
 */
class UdpClient
{
private:
    int sockfd_; // 套接字描述符
    struct sockaddr_in server_addr_;
    struct timeval  timeout_;    // 超时时长
    socklen_t server_addr_len_;    

public:
    UdpClient();
    ~UdpClient();

    // UDP初始化: 重载1, 作为广播客户端, 使用广播地址
    int InitAsBroadcastClient(uint16_t server_port);
    // UDP初始化: 重载2, 作为普通客户端
    int InitAsNormClient(const char* server_ip, uint16_t server_port);
    // UDP初始化: 重载3, 作为组播/多播客户端，这里个人假设客户端发服务端收
    int InitAsMulticastClient(const char* multicast_ip, uint16_t multicast_port);

    // 接收报文
    int Receive(char *buf, int len);
    // 发送报文
    int Send(const char* buf, int len);
};

}
