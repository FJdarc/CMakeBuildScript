import os
import sys
import argparse
import platform
import subprocess
from typing import Optional, Tuple

# 常量定义
DEFAULT_BUILD_DIR = "build"
SUPPORTED_GENERATORS = {
    "Windows": "MinGW Makefiles",
    "Linux": "Unix Makefiles",
    "Darwin": "Unix Makefiles"
}

def parse_arguments() -> argparse.Namespace:
    """解析并验证命令行参数"""
    parser = argparse.ArgumentParser(
        description='CMake cross-platform build automation tool',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        'architecture',
        nargs='?',
        default='x64',
        choices=['x64', 'x86'],
        help="Target architecture:\n"
             "x64 - 64-bit architecture (default)\n"
             "x86 - 32-bit architecture"
    )
    
    parser.add_argument(
        'build_type',
        nargs='?',
        default='d',
        choices=['d', 'r'],
        help="Build configuration:\n"
             "d - Debug build with symbols (default)\n"
             "r - Release build optimized for speed"
    )
    
    parser.add_argument(
        'library_type',
        nargs='?',
        default='st',
        choices=['st', 'sh'],
        help="Library linkage type:\n"
             "st - Static library linkage (default)\n"
             "sh - Shared library/DLL linkage"
    )
    
    parser.add_argument(
        'program_name', 
        nargs='?', 
        default='',
        help="Specify output executable name\n"
             "(default: current directory name)"
    )
    
    return parser.parse_args()

def validate_environment() -> None:
    """检查必要工具的可用性"""
    try:
        subprocess.run(['cmake', '--version'], check=True, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        sys.exit("❌ CMake not found. Please install CMake and add it to PATH")

def get_build_info(args: argparse.Namespace) -> Tuple[str, str, str, str]:
    """生成构建元信息"""
    build_mode = 'Debug' if args.build_type == 'd' else 'Release'
    linkage_type = 'Static' if args.library_type == 'st' else 'Shared'
    compiler_flags = '-m64' if args.architecture == 'x64' else '-m32'
    build_dir = os.path.join(
        DEFAULT_BUILD_DIR,
        f"{args.architecture}-{build_mode.lower()}"
    )
    return build_mode, linkage_type, compiler_flags, build_dir

def configure_project(build_dir: str, build_type: str, 
                     lib_type: str, flags: str) -> bool:
    """执行CMake配置阶段"""
    exec_path = os.path.abspath(os.path.join(build_dir, 'bin'))
    lib_path = os.path.abspath(os.path.join(build_dir, 'lib'))

    cmake_cmd = [
        'cmake',
        '-B', build_dir,
        '-S', '.',
        '-G', SUPPORTED_GENERATORS.get(platform.system(), "Unix Makefiles"),
        f'-DCMAKE_BUILD_TYPE={build_type}',
        f'-DCMAKE_C_FLAGS={flags}',
        f'-DCMAKE_CXX_FLAGS={flags}',
        f'-DEXECUTABLE_OUTPUT_PATH={exec_path}',
        f'-DLIBRARY_OUTPUT_PATH={lib_path}',
        '-DBUILD_SHARED_LIBS=ON' if lib_type == 'Shared' else '-DBUILD_SHARED_LIBS=OFF'
    ]

    try:
        print(f"⚙️  生成构建系统 ({' '.join(cmake_cmd)})")
        subprocess.run(cmake_cmd, check=True)
        print(f"✅ CMake配置成功 [{build_dir}]")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ CMake配置失败: {e}", file=sys.stderr)
        return False

def compile_project(build_dir: str) -> bool:
    """执行代码编译"""
    try:
        print("🔨 开始项目编译...")
        subprocess.run(
            ['cmake', '--build', build_dir, '--parallel'],
            check=True
        )
        print(f"✅ 项目构建成功 [{build_dir}]")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 编译失败: {e}", file=sys.stderr)
        return False

def locate_executable(build_dir: str, 
                     program_name: str) -> Optional[str]:
    """定位生成的可执行文件"""
    base_name = program_name if program_name else os.path.basename(os.getcwd())
    executable = f"{base_name}.exe" if platform.system() == "Windows" else base_name
    exec_path = os.path.join(build_dir, 'bin', executable)
    
    if not os.path.exists(exec_path):
        print(f"⚠️  未找到可执行文件: {exec_path}")
        return None
    return exec_path

def execute_binary(exec_path: str) -> bool:
    """运行编译后的可执行文件"""
    try:
        print(f"🚀 启动程序: {os.path.basename(exec_path)}")
        subprocess.run([exec_path], check=True)
        print("✅ 程序执行成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 程序异常退出 (代码 {e.returncode})", file=sys.stderr)
        return False

def main():
    """主控制流程"""
    args = parse_arguments()
    validate_environment()
    
    build_mode, linkage_type, flags, build_dir = get_build_info(args)
    program_name = args.program_name or os.path.basename(os.getcwd())
    
    print("\n" + "="*50)
    print(f"📂 工作目录: {os.getcwd()}")
    print(f"🖥️  目标架构: {args.architecture.upper()}")
    print(f"⚡ 构建类型: {build_mode}")
    print(f"📚 库类型: {linkage_type}")
    print(f"📁 构建目录: {build_dir}")
    print(f"🎯 目标程序: {program_name}")
    print("="*50 + "\n")

    if not configure_project(build_dir, build_mode, linkage_type, flags):
        sys.exit(1)
    if not compile_project(build_dir):
        sys.exit(1)
    
    if exec_path := locate_executable(build_dir, program_name):
        execute_binary(exec_path)
    
    sys.exit(0)

if __name__ == "__main__":
    main()