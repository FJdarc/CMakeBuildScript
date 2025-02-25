#!/bin/bash

# 解析命令行参数
parse_arguments() {
    Architecture=${1:-x64}
    BuildType=${2:-d}
    ProgramName=$3

    # 校验架构参数
    if [[ "$Architecture" != "x64" && "$Architecture" != "x86" ]]; then
        echo "错误：架构必须是x64或x86" >&2
        exit 1
    fi

    # 校验构建类型
    if [[ "$BuildType" != "d" && "$BuildType" != "r" ]]; then
        echo "错误：构建类型必须是d或r" >&2
        exit 1
    fi

    # 获取程序名
    if [ -z "$ProgramName" ]; then
        ProgramName=$(basename "$PWD")
    fi
}

# 配置CMake
configure_cmake() {
    local build_dir=$1
    local build_type=$2
    local generator=$3
    local arch=$4

    # 创建构建目录和输出目录
    mkdir -p "${build_dir}/bin"
    mkdir -p "${build_dir}/lib"

    # 获取绝对路径
    local exec_path_abs
    exec_path_abs=$(cd "${build_dir}/bin" && pwd)
    local lib_path_abs
    lib_path_abs=$(cd "${build_dir}/lib" && pwd)

    # 执行CMake配置
    echo "正在配置CMake..."
    cmake -B "$build_dir" -S . \
        -DEXECUTABLE_OUTPUT_PATH="$exec_path_abs" \
        -DLIBRARY_OUTPUT_PATH="$lib_path_abs" \
        -DCMAKE_BUILD_TYPE="$build_type" \
        -G "$generator" \
        -DCMAKE_CXX_FLAGS="$arch" \
        -DCMAKE_C_FLAGS="$arch"

    if [ $? -ne 0 ]; then
        echo "❌ CMake配置失败" >&2
        return 1
    fi
    echo "✅ CMake配置成功 @ ${build_dir}"
    return 0
}

# 构建项目
build_project() {
    local build_dir=$1

    echo "正在构建项目..."
    cmake --build "$build_dir"
    if [ $? -ne 0 ]; then
        echo "❌ 项目构建失败" >&2
        return 1
    fi
    echo "✅ 项目构建成功 @ ${build_dir}"
    return 0
}

# 运行可执行文件
run_executable() {
    local exec_path=$1

    if [ ! -f "$exec_path" ]; then
        echo "❌ 可执行文件不存在: ${exec_path}" >&2
        return 1
    fi

    echo "正在运行程序..."
    "$exec_path"
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "❌ 程序执行失败 (exit code ${exit_code})" >&2
        return 1
    fi
    echo "✅ 程序执行成功: ${exec_path}"
    return 0
}

main() {
    parse_arguments "$@"

    # 设置架构参数
    if [ "$Architecture" = "x64" ]; then
        arch="-m64"
    else
        arch="-m32"
    fi

    # 设置构建类型
    if [ "$BuildType" = "d" ]; then
        build_type="Debug"
    else
        build_type="Release"
    fi

    # 构建目录
    build_dir="build/${Architecture}-$( [ "$BuildType" = "d" ] && echo "debug" || echo "release" )"

    # 确定系统和生成器
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*|Windows*)
            generator="MinGW Makefiles"
            exe_suffix=".exe"
            ;;
        Darwin)
            generator="Unix Makefiles"
            exe_suffix=""
            ;;
        Linux)
            generator="Unix Makefiles"
            exe_suffix=""
            ;;
        *)
            echo "未知系统: $(uname -s)" >&2
            exit 1
            ;;
    esac

    # 可执行文件路径
    exec_path="${build_dir}/bin/${ProgramName}${exe_suffix}"

    # 打印信息
    echo "🛠️  工作目录: $PWD"
    echo "🏗️  构建架构: $Architecture"
    echo "🔧 构建类型: $build_type"
    echo "📁 构建目录: $build_dir"
    echo "🚀 目标程序: $ProgramName$exe_suffix"
    echo ""

    # 执行流程
    success=0
    configure_cmake "$build_dir" "$build_type" "$generator" "$arch" || success=1
    if [ $success -eq 0 ]; then
        build_project "$build_dir" || success=1
    fi
    if [ $success -eq 0 ]; then
        run_executable "$exec_path" || success=1
    fi

    exit $success
}

main "$@"