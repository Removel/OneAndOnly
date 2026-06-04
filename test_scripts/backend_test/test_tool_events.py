"""
测试工具调用事件的脚本
"""
import requests
import json

def test_tool_events():
    """测试工具调用事件"""
    
    url = "http://localhost:8000/api/chat-stream"
    
    # 使用一个需要工具的请求
    payload = {
        "human_input": "现在几点了？请告诉我当前时间",
        "session_id": 317486948191043584,
        "clear_history": True
    }
    
    print("开始测试工具调用事件...")
    print(f"请求URL: {url}")
    print(f"请求内容: {json.dumps(payload, ensure_ascii=False)}")
    print("\n" + "="*60)
    print("接收流式响应:")
    print("="*60 + "\n")
    
    try:
        response = requests.post(
            url,
            json=payload,
            stream=True,
            headers={
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            }
        )
        
        if response.status_code == 200:
            print("✓ 连接成功，状态码: 200\n")
            
            full_content = ""
            event_count = 0
            token_count = 0
            tool_start_count = 0
            tool_end_count = 0
            node_start_count = 0
            node_end_count = 0
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    
                    if decoded_line.startswith('event:'):
                        event_type = decoded_line[6:].strip()
                        event_count += 1
                        
                        if event_type == 'token':
                            token_count += 1
                        elif event_type == 'tool_start':
                            tool_start_count += 1
                        elif event_type == 'tool_end':
                            tool_end_count += 1
                        elif event_type == 'node_start':
                            node_start_count += 1
                        elif event_type == 'node_end':
                            node_end_count += 1
                        
                        print(f"[事件 {event_count}] 类型: {event_type}")
                    
                    elif decoded_line.startswith('data:'):
                        data_str = decoded_line[5:].strip()
                        if data_str:
                            try:
                                data = json.loads(data_str)
                                print(f"  数据: {json.dumps(data, ensure_ascii=False)}")
                                
                                if 'content' in data:
                                    full_content += data['content']
                                    print(f"  累计内容长度: {len(full_content)}")
                                
                                if event_type == 'done':
                                    print(f"\n✓ 完成！最终情绪VAC: {data.get('emotion_vac', {})}")
                                    print(f"✓ 重试次数: {data.get('retry_times', 0)}")
                                
                                if event_type == 'error':
                                    print(f"\n✗ 错误: {data.get('message', '未知错误')}")
                            
                            except json.JSONDecodeError as e:
                                print(f"  数据解析失败: {e}")
                    
                    print()
            
            print("="*60)
            print(f"测试完成！共接收 {event_count} 个事件")
            print(f"完整内容长度: {len(full_content)}")
            print("="*60)
            print("\n事件统计:")
            print(f"  Token 事件: {token_count}")
            print(f"  Tool Start 事件: {tool_start_count}")
            print(f"  Tool End 事件: {tool_end_count}")
            print(f"  Node Start 事件: {node_start_count}")
            print(f"  Node End 事件: {node_end_count}")
            print("="*60)
            
            if full_content:
                print("\n完整回复内容:")
                print("-" * 60)
                print(full_content)
                print("-" * 60)
        
        else:
            print(f"✗ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保后端服务已启动")
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tool_events()