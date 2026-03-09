// 本源文件的声明头文件
#include <udpclient.h>
// C/C++系统文件
#include <arpa/inet.h> // inet_addr()
#include <unistd.h>
#include <string.h>
#include <stdio.h>
// 其他库头文件
// 本项目内头文件

namespace utilscpp
{

UdpClient::UdpClient()
{
    sockfd_ = -1;
    // 这里的地址长度是必须初始化的, 作为客户端,服务器地址自己绑定的,要服务器地址长其实没意义
    server_addr_len_ = sizeof(struct sockaddr_in);    
}

UdpClient::~UdpClient()
{
    if (sockfd_ > 0) close(sockfd_);   
}

// UDP初始化: 重载1, 作为广播客户端, 使用广播地址
int UdpClient::InitAsBroadcastClient(uint16_t server_port)
{
    if (sockfd_ > 0) close(sockfd_);

    // 创建套接字
    sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if(sockfd_ < 0){
        perror("create socket failed!\n");
        return -1;
    }
	// 默认的套接字描述符sock是不支持广播，必须设置套接字描述符以支持广播
	int optval = 1;
	setsockopt(sockfd_, SOL_SOCKET, SO_BROADCAST | SO_REUSEADDR, &optval, sizeof(int));
    // 设置发往的服务器的地址与端口
    memset(&server_addr_, 0, sizeof(struct sockaddr_in));
    server_addr_.sin_family = AF_INET;
    server_addr_.sin_port = htons(server_port);
    server_addr_.sin_addr.s_addr = htonl(INADDR_BROADCAST);

    // 超时设置
    timeout_.tv_sec = 1;
    timeout_.tv_usec = 0; // us
    // 设置套接字本身的超时时长 [可选, 如果非阻塞方式设置了select的超时,或就希望程序无数据则阻塞,这里可不选]
    // setsockopt(sockfd_, SOL_SOCKET, SO_RCVTIMEO, (const char*)&timeout_, sizeof(struct timeval));
    return 0;
}
// UDP初始化: 重载2, 作为普通客户端
int UdpClient::InitAsNormClient(const char* server_ip, uint16_t server_port)
{
    if (sockfd_ > 0) close(sockfd_);

    // 创建套接字
    sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if(sockfd_ < 0){
        perror("create socket failed!\n");
        return -1;
    }
    // 设置发往的服务器的地址与端口
    memset(&server_addr_, 0, sizeof(struct sockaddr_in));
    server_addr_.sin_family = AF_INET;
    server_addr_.sin_port = htons(server_port);
    server_addr_.sin_addr.s_addr = inet_addr(server_ip);// htonl(INADDR_ANY);

    // 设置套接字本身的超时时长 [可选, 如果非阻塞方式设置了select的超时,或就希望程序无数据则阻塞,这里可不选]
    // setsockopt(sockfd_, SOL_SOCKET, SO_RCVTIMEO, (const char*)&timeout_, sizeof(struct timeval));
    return 0;
}

// UDP初始化: 重载3, 作为组播/多播客户端，这里个人假设客户端发服务端收
int UdpClient::InitAsMulticastClient(const char* multicast_ip, uint16_t multicast_port)
{
    if (sockfd_ > 0) close(sockfd_);

    // 创建套接字
    sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if(sockfd_ < 0){
        perror("create socket failed!\n");
        return -1;
    }

    // 指定ip及端口，初始化相关结构体
    // 组地址相当于一般模式下的服务端地址，设置组播地址与端口
    memset(&server_addr_, 0, sizeof(sockaddr_in));
    server_addr_.sin_family = AF_INET;
    server_addr_.sin_port = htons(multicast_port);   // 指定监听端口, htons将一个无符号短整型数值转换为网络字节序
    server_addr_.sin_addr.s_addr = inet_addr(multicast_ip); // 将主机的无符号长整形数转换成网络字节顺序

    return 0;
}

int UdpClient::Receive(char* buf, int len) 
{
    // 非阻塞方式读取，read与recvfrom等都是阻塞函数，用select实现非阻塞编程, 以及多路复用(这里意为多个套接字收发)
    // 文件描述符集合: 包含可读\可写\异常文件描述符3类
    // fd范围0-1023, 3以上可分配给sockfd, 0表示标准输入，1表示标准输出，2表示标准错误输出
    // sizeof(fd_set)为128字节,1024bit,每bit标识一个文件描述符状态, fd取值与实际对应的bit位序号差,故select的时候要+1
    // 全套流程为: 1. 先清空再把当前sockfd加进去,select的时候查看read来的数据是不是这个套接字的,是则readSet对应bit置位
    // 2. select在规定时间(取NULL则阻塞)内如果没有收到,返回0超时
    // // 超时设置
    // timeout_.tv_sec = 2;
    // timeout_.tv_usec = 0; // us
    // fd_set readset;
    // // 清空套接字集合
    // FD_ZERO(&readset);
    // // 套接字描述符加入文件描述符集合
    // FD_SET(sockfd_, &readset);
    // int ret = select(sockfd_ + 1, &readset, NULL, NULL, &timeout_); // timeout_ 取 NULL则select阻塞
    // if (ret <= 0)   // -1出错 0超时
    // {
    //     perror("UDPCLENT：SOCKET select error\n Or UDPCLENT:UDP recv time out!\n");
    //     return -1;
    // }
    // // 检查sockfd在集合readfd当中的状态是否变化(被置位)
    // if (!FD_ISSET(sockfd_, &readset))
    // {
    //     perror("UDP socket not in readset\n");
    //     return -1;
    // }

    int num_bytes = recvfrom(sockfd_, buf, len, 0, (struct sockaddr*)&server_addr_, &server_addr_len_);  // 第5参返回发送端的地址信息
    if (num_bytes <= 0){
        perror("UDP Recv failed\n");
        return -1;
    }
    return num_bytes;    
}

int UdpClient::Send(const char* buf, int len)
{
    int num_bytes = sendto(sockfd_, buf, len, 0, (struct sockaddr*)&server_addr_, sizeof(struct sockaddr));
    if (num_bytes < 0){
        perror("UDP send failed\n");
        return -1;
    }
    return num_bytes;
}

}
