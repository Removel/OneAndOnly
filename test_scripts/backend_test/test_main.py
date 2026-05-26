"""
后端测试主入口
运行所有后端测试：数据库测试和API接口测试
"""
import sys
import os
import subprocess
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_scripts.backend_test.test_database import test_database
from test_scripts.backend_test.test_api import run_all_tests


def run_database_test():
    """运行数据库测试"""
    print("\n")
    print("*" * 50)
    print("开始数据库测试")
    print("*" * 50)
    
    try:
        test_database()
        print("\n数据库测试完成")
        return True
    except Exception as e:
        print(f"\n数据库测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_api_test():
    """运行API测试"""
    print("\n")
    print("*" * 50)
    print("开始API测试")
    print("*" * 50)
    
    try:
        run_all_tests()
        print("\nAPI测试完成")
        return True
    except Exception as e:
        print(f"\nAPI测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_backend_running():
    """检查后端服务是否正在运行"""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_backend_server():
    """启动后端服务器"""
    print("\n正在启动后端服务器...")
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    backend_main = os.path.join(project_root, "backend", "main.py")
    
    try:
        # 使用subprocess启动后端服务器
        process = subprocess.Popen(
            [sys.executable, backend_main],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        # 等待服务器启动
        max_wait = 10
        for i in range(max_wait):
            time.sleep(1)
            if check_backend_running():
                print(f"后端服务器启动成功 (PID: {process.pid})")
                return process
        
        print("后端服务器启动超时")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"启动后端服务器失败: {str(e)}")
        return None


def stop_backend_server(process):
    """停止后端服务器"""
    if process:
        print(f"\n正在停止后端服务器 (PID: {process.pid})...")
        process.terminate()
        try:
            process.wait(timeout=5)
            print("后端服务器已停止")
        except subprocess.TimeoutExpired:
            process.kill()
            print("强制停止后端服务器")


def main():
    """主函数"""
    print("\n")
    print("=" * 50)
    print("One and Only 后端测试套件")
    print("=" * 50)
    
    # 询问用户要运行哪些测试
    print("\n请选择要运行的测试:")
    print("1. 数据库测试")
    print("2. API接口测试")
    print("3. 全部测试")
    print("4. 退出")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "1":
        run_database_test()
    elif choice == "2":
        if not check_backend_running():
            print("\n后端服务未运行，正在启动...")
            backend_process = start_backend_server()
            if backend_process:
                try:
                    run_api_test()
                finally:
                    stop_backend_server(backend_process)
            else:
                print("无法启动后端服务，请手动启动后端服务后再试")
        else:
            print("\n检测到后端服务正在运行")
            run_api_test()
    elif choice == "3":
        # 运行数据库测试
        db_success = run_database_test()
        
        # 运行API测试
        print("\n")
        backend_process = None
        if not check_backend_running():
            print("后端服务未运行，正在启动...")
            backend_process = start_backend_server()
        
        if backend_process or check_backend_running():
            try:
                api_success = run_api_test()
            finally:
                if backend_process:
                    stop_backend_server(backend_process)
        else:
            print("无法启动后端服务，跳过API测试")
            api_success = False
        
        # 总结测试结果
        print("\n")
        print("=" * 50)
        print("测试总结")
        print("=" * 50)
        print(f"数据库测试: {'✓ 通过' if db_success else '✗ 失败'}")
        print(f"API测试: {'✓ 通过' if api_success else '✗ 失败'}")
        print("=" * 50)
    elif choice == "4":
        print("退出测试")
        return
    else:
        print("无效选项")


if __name__ == "__main__":
    main()