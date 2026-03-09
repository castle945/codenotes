// 本源文件的声明头文件
#include <udpserver.h>
// C/C++系统文件
#include <arpa/inet.h> // inet_addr()
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <fcntl.h>
// 其他库头文件
// 本项目内头文件

namespace utilscpp
{

UdpServer::UdpServer()
{
    sockfd_ = -1;
    client_addr_len_ = sizeof(struct sockaddr_in);
}

UdpServer::~UdpServer()
{
    if (sockfd_ > 0) close(sockfd_);
}

// UDP初始化: 重载1, 作为多播服务端/接收端, 使用多播地址
int UdpServer::InitAsMulticastServer(const char* device_ip, const char* multicast_ip, uint16_t multicast_port)
{
    if (sockfd_ > 0) close(sockfd_);  
    
    // 创建套接字
    sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if(sockfd_ < 0){
        perror("create socket failed!\n");
        return -1;
    }

	// 默认的套接字描述符sock是不支持多播，必须设置套接字描述符以支持多播，这里可以挨个打印状态进行调试
	int optval = 1;
	setsockopt(sockfd_, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(int));
    optval = fcntl(sockfd_, F_GETFL);
    fcntl(sockfd_, F_SETFL, optval);

    memset(&server_addr_, 0, sizeof(struct sockaddr_in));
    server_addr_.sin_family = AF_INET;
    server_addr_.sin_port = htons(multicast_port);
    server_addr_.sin_addr.s_addr = inet_addr(multicast_ip);;
    if (bind(sockfd_, (struct sockaddr*)&server_addr_, sizeof(server_addr_)) < 0) {perror("bind multicast failed\n"); return -1;}

    // 加入该IP的组播组，才能在组内接收数据
    struct ip_mreq ipMreq;
	ipMreq.imr_interface.s_addr = inet_addr(device_ip);
	ipMreq.imr_multiaddr.s_addr = inet_addr(multicast_ip);
	if(setsockopt(sockfd_, IPPROTO_IP, IP_ADD_MEMBERSHIP, &ipMreq, sizeof(ipMreq)) != 0) {perror("add multicast membership failed\n"); return -1;}

    return 0;
}

// UDP初始化: 重载2, 作为普通服务端，使用本机地址
int UdpServer::Initialize(uint16_t  server_port)
{
    if (sockfd_ > 0) close(sockfd_);  
    
    // 创建套接字
    sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if(sockfd_ < 0){
        perror("create socket failed!\n");
        return -1;
    }

    // 指定ip及端口，初始化相关结构体,注意这里MC是服务器端
    memset(&server_addr_, 0, sizeof(sockaddr_in));
    server_addr_.sin_family = AF_INET;
    server_addr_.sin_port = htons(server_port);   // 指定监听端口, htons将一个无符号短整型数值转换为网络字节序
    // 指定服务器地址, INADDR_ANY为0.0.0.0的地址，表示不确定地址，或“所有地址”、“任意地址”, 这里即表示不关心服务器地址,事实上是本机localhost
    server_addr_.sin_addr.s_addr = htonl(INADDR_ANY); // 将主机的无符号长整形数转换成网络字节顺序

    // 超时设置
    timeout_.tv_sec = 2;
    timeout_.tv_usec = 0; // us
    // 设置套接字本身的超时时长 [可选, 如果非阻塞方式设置了select的超时,或就希望程序无数据则阻塞,这里可不选]
    // setsockopt(sockfd_, SOL_SOCKET, SO_RCVTIMEO, (const char*)&timeout_, sizeof(struct timeval));

    // 服务器端绑定端口
    int ret = bind(sockfd_, (struct sockaddr*)&(server_addr_), sizeof(server_addr_));
    if (ret < 0){
        perror("bind socket faild!\n");
        return -1;
    }
    return 0;
}

// 接收报文
int UdpServer::Receive(char *buf, int len)
{
    // 非阻塞方式读取，read与recvfrom等都是阻塞函数，用select实现非阻塞编程, 以及多路复用(这里意为多个套接字收发)
    // 文件描述符集合: 包含可读\可写\异常文件描述符3类
    // fd范围0-1023, 3以上可分配给sockfd, 0表示标准输入，1表示标准输出，2表示标准错误输出
    // sizeof(fd_set)为128字节,1024bit,每bit标识一个文件描述符状态, fd取值与实际对应的bit位序号差,故select的时候要+1
    // 全套流程为: 1. 先清空再把当前sockfd加进去,select的时候查看read来的数据是不是这个套接字的,是则readSet对应bit置位
    // 2. select在规定时间(取NULL则阻塞)内如果没有收到,返回0超时
    // fd_set readSet;
    // // 清空套接字集合
    // FD_ZERO(&readSet);
    // // 套接字描述符加入文件描述符集合
    // FD_SET(sockfd_, &readSet);
    // int ret = select(sockfd_ + 1, &readSet, NULL, NULL, &timeout_); // timeout_ 取 NULL则select阻塞
    // if (ret <= 0)   // -1出错 0超时
    // {
    //     perror("UdpServer: select error\n Or recv time out!\n");
    //     return -1;
    // }
    // // 检查sockfd在集合readfd当中的状态是否变化(被置位)
    // if (!FD_ISSET(sockfd_, &readSet))
    // {
    //     perror("UDP socket not in readSet\n");
    //     return -1;
    // }

    int nBytes = recvfrom(sockfd_, buf, len, 0, (struct sockaddr*)&client_addr_, &client_addr_len_);
    if (nBytes <= 0){
        perror("UDP Recv failed\n");
        return -1;
    }
    return nBytes;
}
// 发送报文
int UdpServer::Send(const char* buf, int len)
{
    // 
    int nBytes = sendto(sockfd_, buf, len, 0, (struct sockaddr*)&client_addr_, sizeof(struct sockaddr));
    if (nBytes < 0){
        perror("UDP send failed\n");
        return -1;
    }
    return nBytes;
}
}