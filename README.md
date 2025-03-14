# ​CMake一键运行程序

## Purpose

不需要编译器配置文件即可运行CMake项目

支持指定编译架构，编译类型，库类型和程序名称

## Run

默认使用gcc和g++

需要安装CMake

Windows下推荐安装[MinGW](https://github.com/niXman/mingw-builds-binaries/releases)

下载程序[Cbs.py](https://github.com/FJdarc/CMakeBuildScript/blob/master/Cbs.py)

移动到CMake项目根CMakeLists.txt目录

执行命令 `x86_64-Cbs.py -h`

得到帮助信息如下
```bash
usage: Cbs.py [-h] [-a [{x64,x86}]] [-b [{d,r}]] [-l [{st,sh}]] [-p [PROGRAM_NAME]]

CMake项目构建工具

options:
  -h, --help            显示帮助信息并退出
  -a, --architecture [{x64,x86}]
                        目标架构:
                        x64 - 64位架构 (默认)
                        x86 - 32位架构
  -b, --build-type [{d,r}]
                        构建类型:
                        d - 调试版本 (默认)
                        r - 发布版本
  -l, --library-type [{st,sh}]
                        库类型:
                        st - 静态库 (默认)
                        sh - 动态库/DLL
  -p, --program-name [PROGRAM_NAME]
                        指定运行程序名称 (默认使用当前目录名)
```