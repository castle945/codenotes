# C++ 编译相关

### g++ 编译

- 见 `main.cpp`： `-I./include` 指定头文件路径，`-L./lib`指定第三方库链接路径，`-lglog`指定链接库名

### cmake 编译

- `cmake_module` ：自定义的 cmake 模块文件，其中 `ALL_TARGET_LIBRARIES` 为自定义变量，最好搭配模板代码的 `CMakeLists.txt` 使用
- `cmake_template`：cmake 项目的模板代码

  ```bash
  mkdir build ; cd build ; cmake .. ; make
  ./main
  ./udpserver_loop
  # socat UDP4-LISTEN:54321 - # 或者命令行工具监听端口
  ```
