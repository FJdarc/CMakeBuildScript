#!/bin/bash

# 设置严格模式
set -euo pipefail

# 格式化输出颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 解析命令行参数
parse_arguments() {
    build_type="d"
    program_name=""
    
    # 第一个参数是构建类型
    if [[ $# -ge 1 ]]; then
        if [[ $1 =~ ^(d|r)$ ]]; then
            build_type=$1
        else
            # 如果第一个参数不是构建类型，则视为程序名
            program_name=$1
            build_type="d"
        fi
    fi
    
    # 第二个参数是程序名
    if [[ $# -ge 2 ]]; then
        program_name=$2
    fi
    
    # 设置默认程序名为当前目录名
    if [[ -z $program_name ]]; then
        program_name=$(basename "$PWD")
    fi
}

# 执行CMake配置
configure_cmake() {
    local build_dir=$1
    local build_type=$2
    local exec_path=$(realpath "$build_dir/bin")
    local lib_path=$(realpath "$build_dir/lib")

    echo -e "${YELLOW}🛠️  配置CMake...${NC}"
    if cmake -B "$build_dir" -S . \
        -DEXECUTABLE_OUTPUT_PATH="$exec_path" \
        -DLIBRARY_OUTPUT_PATH="$lib_path" \
        -DCMAKE_BUILD_TYPE="$build_type"; then
        echo -e "${GREEN}✅ CMake 配置成功 @ $build_dir${NC}"
        return 0
    else
        echo -e "${RED}❌ CMake 配置失败${NC}" >&2
        return 1
    fi
}

# 构建项目
build_project() {
    local build_dir=$1

    echo -e "${YELLOW}🔨 构建项目...${NC}"
    if cmake --build "$build_dir"; then
        echo -e "${GREEN}✅ 项目构建成功 @ $build_dir${NC}"
        return 0
    else
        echo -e "${RED}❌ 项目构建失败${NC}" >&2
        return 1
    fi
}

# 运行可执行文件
run_executable() {
    local exec_path=$1

    echo -e "${YELLOW}🚀 启动程序...${NC}"
    if [[ ! -f $exec_path ]]; then
        echo -e "${RED}❌ 可执行文件不存在: $exec_path${NC}" >&2
        return 1
    fi

    if "$exec_path"; then
        echo -e "${GREEN}✅ 程序执行成功: $exec_path${NC}"
        return 0
    else
        local exit_code=$?
        echo -e "${RED}❌ 程序执行失败 (exit code $exit_code)${NC}" >&2
        return $exit_code
    fi
}

main() {
    parse_arguments "$@"
    
    # 初始化路径参数
    local build_type_full="Debug"
    [[ $build_type == "r" ]] && build_type_full="Release"
    
    local build_dir="out/"
    [[ $build_type == "d" ]] && build_dir+="debug" || build_dir+="release"
    
    local exec_path="$build_dir/bin/$program_name"

    # 显示构建信息
    echo -e "${YELLOW}=============================${NC}"
    echo -e "${GREEN}🛠️  当前目录: ${YELLOW}$PWD${NC}"
    echo -e "${GREEN}🔧 构建类型: ${YELLOW}$build_type_full${NC}"
    echo -e "${GREEN}📁 构建目录: ${YELLOW}$build_dir${NC}"
    echo -e "${GREEN}🚀 目标程序: ${YELLOW}$program_name${NC}"
    echo -e "${YELLOW}=============================${NC}"

    # 创建构建目录
    mkdir -p "$build_dir"

    # 执行完整流程
    if configure_cmake "$build_dir" "$build_type_full" && \
       build_project "$build_dir" && \
       run_executable "$exec_path"; then
        exit 0
    else
        exit 1
    fi
}

# 执行主函数
main "$@"