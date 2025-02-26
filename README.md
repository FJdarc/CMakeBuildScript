## CMake项目构建工具

curl -O https://raw.githubusercontent.com/FJdarc/CMakeBuildScript/master/Cbs.py | chmod +x ./Cbs.py

usage: Cbs.py [-h] [{x64,x86}] [{d,r}] [{st,sh}] [program_name]

CMake项目构建工具

positional arguments:
  {x64,x86}     目标架构:
                x64 - 64位架构 (默认)
                x86 - 32位架构
  {d,r}         构建类型:
                d - 调试版本 (默认)
                r - 发布版本
  {st,sh}       库类型:
                st - 静态库 (默认)
                sh - 动态库/DLL
  program_name  指定输出程序名称 (默认使用当前目录名)

options:
  -h, --help    show this help message and exit