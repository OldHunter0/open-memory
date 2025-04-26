from .api import run_api
import argparse

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5002)
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    
    print(f"启动参数 - 端口: {args.port}, Host: {args.host}, Debug: {args.debug}")  # 调试输出
    
    run_api(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()