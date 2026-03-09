///////////////////////////////////////////////////////////////////////////////
///
/// @copyright Copyright (C), 2021, 南京理工大学计算机科学与工程学院, 智能科学与技术系
/// @file      udpserver.h
/// @author    谢城
/// @date      2021-09-27
/// @brief     Udp做服务端的封装
///          
///////////////////////////////////////////////////////////////////////////////
#pragma once

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdint.h>

namespace utilscpp {

/**
 * Udp服务端类
 */
class UdpServer
{
private:
    // 套接字描述符
    int sockfd_; 
    struct sockaddr_in server_addr_;
    struct timeval  timeout_;    // 超时时长
    socklen_t client_addr_len_;
    // 输出, 从接收的报文里获取的客户端地址
    struct sockaddr_in client_addr_;
public:

    UdpServer();
    ~UdpServer();

    // UDP初始化: 重载1, 作为多播服务端/接收端, 使用多播地址
    int InitAsMulticastServer(const char* device_ip, const char* multicast_ip, uint16_t multicast_port);
    // UDP初始化: 重载2, 作为普通服务端，使用本机地址
    int Initialize(uint16_t  server_port);
    // 接收报文
    int Receive(char *buf, int len);
    // 发送报文
    int Send(const char* buf, int len);

    struct sockaddr_in client_addr() { return client_addr_; }
};

}
