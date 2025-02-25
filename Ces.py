import os
import sys
import argparse
import platform
import subprocess

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='CMake cross-platform build script',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'Architecture',
        nargs='?',
        default='x64',
        choices=['x64', 'x86'],
        help="Architecture: 'x64' (default) or 'x86'"
    )
    parser.add_argument(
        'BuildType',
        nargs='?',
        default='d',
        choices=['d', 'r'],
        help="Build type: 'd' (Debug, default) or 'r' (Release)"
    )
    parser.add_argument(
        'ProgramName', 
        nargs='?', 
        default='',
        help="Name of the executable to run (default: current directory)"
    )
    return parser.parse_args()

def get_program_name(user_input):
    """获取程序名称（优先使用用户输入）"""
    return user_input if user_input else os.path.basename(os.getcwd())

def configure_cmake(arch, build_dir, build_type, generator):
    """执行CMake配置"""
    exec_path = os.path.abspath(os.path.join(build_dir, 'bin'))
    lib_path = os.path.abspath(os.path.join(build_dir, 'lib'))

    config = [
            'cmake',
            '-B', build_dir,
            '-S', '.',
            f'-DEXECUTABLE_OUTPUT_PATH={exec_path}',
            f'-DLIBRARY_OUTPUT_PATH={lib_path}',
            f'-DCMAKE_BUILD_TYPE={build_type}',
        ]
    config.append('-G')
    config.append(generator)
    config.append(f'-DCMAKE_CXX_FLAGS={arch}')
    config.append(f'-DCMAKE_C_FLAGS={arch}')
    try:
        subprocess.run(config, check=True)
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
    
    arch = "-m64" if args.Architecture == 'x64' else "-m32"
    build_type = 'Debug' if args.BuildType == 'd' else 'Release'
    build_dir = os.path.join('build', str(args.Architecture) + '-debug' if args.BuildType == 'd' else str(args.Architecture) + '-release')
    program_name = get_program_name(args.ProgramName)
    exec_path = os.path.join(build_dir, 'bin', program_name)
    generator = 'Unix Makefiles'

    system = platform.system()
    if system == "Windows":
        print('Windows')
        program_name +=".exe"
        generator = 'MinGW Makefiles'
    elif system == "Linux":
        print('Linux')
    elif system == "Darwin":
        print('MacOS')
    else:
        print('Unknown System')

    print(f"🛠️  工作目录: {os.getcwd()}")
    print(f"🏗️  构建架构: {args.Architecture}")
    print(f"🔧 构建类型: {build_type}")
    print(f"📁 构建目录: {build_dir}")
    print(f"🚀 目标程序: {program_name}\n")

    # 执行完整流程
    success = configure_cmake(arch, build_dir, build_type, generator) \
        and build_project(build_dir) \
        and run_executable(exec_path)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()