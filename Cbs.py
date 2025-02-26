#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
import platform
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List

# ANSI转义码常量
COLORS = {
    "RESET": '\033[0m',
    "BOLD": '\033[1m',
    "RED": '\033[31m',
    "GREEN": '\033[32m',
    "YELLOW": '\033[33m',
    "BLUE": '\033[34m',
    "CYAN": '\033[36m',
    "WHITE": '\033[37m'
}

# 日志样式配置
LOG_STYLE = {
    "TITLE": f"{COLORS['WHITE']}{COLORS['BOLD']}",
    "HEADER": f"{COLORS['CYAN']}{COLORS['BOLD']}",
    "INFO": COLORS["BLUE"],
    "SUCCESS": f"{COLORS['GREEN']}{COLORS['BOLD']}",
    "WARNING": COLORS["YELLOW"],
    "ERROR": f"{COLORS['RED']}{COLORS['BOLD']}",
    "TIME": COLORS["CYAN"]
}

# 常量定义
DEFAULT_BUILD_DIR = "build"
SUPPORTED_GENERATORS = {
    "Windows": "MinGW Makefiles",
    "Linux": "Unix Makefiles",
    "Darwin": "Unix Makefiles"
}

def enable_windows_ansi() -> None:
    """启用Windows ANSI转义码支持"""
    if sys.platform == "win32":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    class CustomHelpAction(argparse.Action):
        def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, help=None):
            super().__init__(
                option_strings=option_strings,
                dest=dest,
                default=default,
                nargs=0,
                help=help
            )
        
        def __call__(self, parser, namespace, values, option_string=None):
            parser.print_help()
            input(f"\n{LOG_STYLE['INFO']}🔚 按任意键退出...{COLORS['RESET']}")
            sys.exit(0)

    parser = argparse.ArgumentParser(
        description=f'{LOG_STYLE["HEADER"]}CMake项目构建工具{COLORS["RESET"]}',
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False  # 禁用默认的help处理
    )
    
    # 添加自定义help选项
    parser.add_argument(
        '-h', '--help',
        action=CustomHelpAction,
        help='显示帮助信息并退出'
    )
    
    help_text = {
        "arch": (
            "目标架构:\n"
            "x64 - 64位架构 (默认)\n"
            "x86 - 32位架构"
        ),
        "build_type": (
            "构建类型:\n"
            "d - 调试版本 (默认)\n"
            "r - 发布版本"
        ),
        "lib_type": (
            "库类型:\n"
            "st - 静态库 (默认)\n"
            "sh - 动态库/DLL"
        ),
        "program": "指定输出程序名称 (默认使用当前目录名)"
    }
    
    # 原有参数定义保持不变
    parser.add_argument(
        'architecture',
        nargs='?',
        default='x64',
        choices=['x64', 'x86'],
        help=f"{LOG_STYLE['INFO']}{help_text['arch']}{COLORS['RESET']}"
    )
    
    parser.add_argument(
        'build_type',
        nargs='?',
        default='d',
        choices=['d', 'r'],
        help=f"{LOG_STYLE['INFO']}{help_text['build_type']}{COLORS['RESET']}"
    )
    
    parser.add_argument(
        'library_type',
        nargs='?',
        default='st',
        choices=['st', 'sh'],
        help=f"{LOG_STYLE['INFO']}{help_text['lib_type']}{COLORS['RESET']}"
    )
    
    parser.add_argument(
        'program_name', 
        nargs='?', 
        default='',
        help=f"{LOG_STYLE['INFO']}{help_text['program']}{COLORS['RESET']}"
    )
    
    return parser.parse_args()

def check_compiler(name: str, command: List[str]) -> None:
    """验证编译器是否存在"""
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        sys.exit(f"{LOG_STYLE['ERROR']}❌ {name}未找到: {e}{COLORS['RESET']}")

def validate_environment() -> None:
    """验证构建环境"""
    try:
        subprocess.run(
            ['cmake', '--version'],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        sys.exit(f"{LOG_STYLE['ERROR']}❌ CMake未找到: {e}{COLORS['RESET']}")
    
    # 检查编译工具链
    for compiler in [('GCC', ['gcc', '--version']), ('G++', ['g++', '--version'])]:
        check_compiler(*compiler)

def get_build_params(args: argparse.Namespace) -> Tuple[str, str, str, Path]:
    """获取构建配置参数"""
    build_mode = 'Debug' if args.build_type == 'd' else 'Release'
    linkage_type = 'Static' if args.library_type == 'st' else 'Shared'
    compiler_flags = '-m64' if args.architecture == 'x64' else '-m32'
    build_dir = Path(DEFAULT_BUILD_DIR) / f"{args.architecture}-{build_mode.lower()}"
    return build_mode, linkage_type, compiler_flags, build_dir

def run_command(command: List[str], description: str, error_msg: str) -> Tuple[bool, float]:
    """通用命令执行函数"""
    print(f"{LOG_STYLE['INFO']}⚙️  {description}{COLORS['RESET']}")
    start_time = time.perf_counter()
    success = False
    try:
        subprocess.run(command, check=True)
        success = True
    except subprocess.CalledProcessError as e:
        print(f"{LOG_STYLE['ERROR']}❌ {error_msg}: {e}{COLORS['RESET']}")
        input(f"\n{LOG_STYLE['INFO']}🔚 按任意键退出...{COLORS['RESET']}")
    return success, time.perf_counter() - start_time

def configure_project(build_dir: Path, build_type: str, lib_type: str, flags: str) -> Tuple[bool, float]:
    """执行CMake配置"""
    exec_path = build_dir / 'bin'
    lib_path = build_dir / 'lib'

    cmake_cmd = [
        'cmake',
        '-B', str(build_dir),
        '-S', '.',
        '-G', SUPPORTED_GENERATORS.get(platform.system(), "Unix Makefiles"),
        f'-DCMAKE_BUILD_TYPE={build_type}',
        f'-DCMAKE_C_FLAGS={flags}',
        f'-DCMAKE_CXX_FLAGS={flags}',
        f'-DEXECUTABLE_OUTPUT_PATH={exec_path.resolve()}',
        f'-DLIBRARY_OUTPUT_PATH={lib_path.resolve()}',
        '-DBUILD_SHARED_LIBS=ON' if lib_type == 'Shared' else '-DBUILD_SHARED_LIBS=OFF'
    ]
    
    return run_command(
        cmake_cmd,
        f"生成构建系统: {' '.join(cmake_cmd)}",
        "CMake配置失败"
    )

def compile_project(build_dir: Path) -> Tuple[bool, float]:
    """执行项目编译"""
    return run_command(
        ['cmake', '--build', str(build_dir), '--parallel'],
        "开始项目编译...",
        "编译失败"
    )

def locate_executable(build_dir: Path, program_name: str) -> Optional[Path]:
    """定位生成的可执行文件"""
    base_name = program_name if program_name else Path.cwd().name
    executable = f"{base_name}.exe" if platform.system() == "Windows" else base_name
    exec_path = build_dir / 'bin' / executable
    
    if not exec_path.exists():
        print(f"{LOG_STYLE['WARNING']}⚠️  未找到可执行文件: {exec_path}{COLORS['RESET']}")
        return None
    return exec_path

def execute_binary(exec_path: Path) -> bool:
    """运行可执行程序"""
    try:
        print(f"{LOG_STYLE['INFO']}🚀 启动程序: {exec_path.name}{COLORS['RESET']}")
        subprocess.run([str(exec_path)], check=True)
        print(f"{LOG_STYLE['SUCCESS']}✅ 程序执行成功{COLORS['RESET']}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{LOG_STYLE['ERROR']}❌ 程序异常退出 (代码 {e.returncode}){COLORS['RESET']}")
        return False

def main() -> None:
    """主流程"""
    enable_windows_ansi()
    args = parse_arguments()
    validate_environment()
    
    build_mode, linkage_type, flags, build_dir = get_build_params(args)
    program_name = args.program_name or Path.cwd().name
    
    # 打印构建头信息
    header = [
        "="*50,
        f"📂 工作目录: {Path.cwd()}",
        f"🖥️  目标架构: {args.architecture.upper()}",
        f"⚡ 构建类型: {build_mode}",
        f"📚 库类型: {linkage_type}",
        f"📁 构建目录: {build_dir}",
        f"🎯 目标程序: {program_name}",
        "="*50
    ]
    print(f"{LOG_STYLE['TITLE']}" + "\n".join(header) + f"{COLORS['RESET']}\n")

    # 配置阶段
    config_success, config_time = configure_project(build_dir, build_mode, linkage_type, flags)
    if not config_success:
        print(f"{LOG_STYLE['TIME']}⏱️  CMake配置耗时: {config_time:.2f}秒{COLORS['RESET']}")
        sys.exit(1)
    print(f"{LOG_STYLE['SUCCESS']}✅ CMake配置成功{COLORS['RESET']} {LOG_STYLE['TIME']}| 耗时: {config_time:.2f}秒{COLORS['RESET']}")

    # 编译阶段
    compile_success, compile_time = compile_project(build_dir)
    if not compile_success:
        print(f"{LOG_STYLE['TIME']}⏱️  编译耗时: {compile_time:.2f}秒{COLORS['RESET']}")
        sys.exit(1)
    print(f"{LOG_STYLE['SUCCESS']}✅ 项目构建成功{COLORS['RESET']} {LOG_STYLE['TIME']}| 耗时: {compile_time:.2f}秒{COLORS['RESET']}")
    print(f"{LOG_STYLE['TIME']}🏁 总构建时间: {config_time + compile_time:.2f}秒{COLORS['RESET']}\n")

    # 运行程序
    if exec_path := locate_executable(build_dir, program_name):
        execute_binary(exec_path)
        
    input(f"\n{LOG_STYLE['INFO']}🔚 按任意键退出...{COLORS['RESET']}")
    sys.exit(0)

if __name__ == "__main__":
    main()