import argparse
import os
import subprocess
import sys
import platform

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Build and run a CMake project.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'build_type', 
        nargs='?', 
        default='d', 
        choices=['d', 'r'],
        help="Build type: 'd' for debug (default), 'r' for release"
    )
    parser.add_argument(
        'program_name', 
        nargs='?', 
        default=None,
        help="Program name (default: current directory name)"
    )
    return parser.parse_args()

def get_program_name(user_input):
    """获取程序名称（优先使用用户输入）"""
    return user_input if user_input else os.path.basename(os.getcwd())

def configure_cmake(build_dir, build_type):
    """执行CMake配置"""
    exec_path = os.path.abspath(os.path.join(build_dir, 'bin'))
    lib_path = os.path.abspath(os.path.join(build_dir, 'lib'))

    try:
        subprocess.run([
            'cmake',
            '-B', build_dir,
            '-S', '.',
            '-G', 'MinGW Makefiles',
            f'-DEXECUTABLE_OUTPUT_PATH={exec_path}',
            f'-DLIBRARY_OUTPUT_PATH={lib_path}',
            f'-DCMAKE_BUILD_TYPE={build_type}',
        ], check=True)
        print(f"✅ CMake 配置成功 @ {build_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ CMake 配置失败: {e}", file=sys.stderr)
        return False

def build_project(build_dir):
    """执行项目构建"""
    try:
        subprocess.run(['cmake', '--build', build_dir], check=True)
        print(f"✅ 项目构建成功 @ {build_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 项目构建失败: {e}", file=sys.stderr)
        return False

def run_executable(exec_path):
    """运行生成的可执行文件"""
    if not os.path.exists(exec_path):
        print(f"❌ 可执行文件不存在: {exec_path}", file=sys.stderr)
        return False

    try:
        subprocess.run([exec_path], check=True)
        print(f"✅ 程序执行成功: {exec_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 程序执行失败 (exit code {e.returncode})", file=sys.stderr)
        return False

def main():
    """主工作流程"""
    args = parse_arguments()
    
    # 初始化路径参数
    build_type = 'Debug' if args.build_type == 'd' else 'Release'
    build_dir = os.path.join('out', 'debug' if args.build_type == 'd' else 'release')
    program_name = get_program_name(args.program_name)
    system = platform.system()
    if system == "Windows":
        program_name += ".exe"
    exec_path = os.path.join(build_dir, 'bin', program_name)

    print(f"🛠️  当前目录: {os.getcwd()}")
    print(f"🔧 构建类型: {build_type}")
    print(f"📁 构建目录: {build_dir}")
    print(f"🚀 目标程序: {program_name}")

    # 执行完整流程
    success = configure_cmake(build_dir, build_type) \
        and build_project(build_dir) \
        and run_executable(exec_path)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()