import asyncio
import requests
import json

async def test_stream_chat():
    """测试流式聊天功能"""
    
    url = "http://localhost:8000/api/chat-stream"
    
    payload = {
        "human_input": "你好，请介绍一下你自己",
        "session_id": 317486948191043584,
        "clear_history": True
    }
    
    print("开始测试流式聊天...")
    print(f"请求URL: {url}")
    print(f"请求内容: {json.dumps(payload, ensure_ascii=False)}")
    print("\n" + "="*50)
    print("接收流式响应:")
    print("="*50 + "\n")
    
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
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    
                    if decoded_line.startswith('event:'):
                        event_type = decoded_line[6:].strip()
                        event_count += 1
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
            
            print("="*50)
            print(f"测试完成！共接收 {event_count} 个事件")
            print(f"完整内容长度: {len(full_content)}")
            print("="*50)
            
            if full_content:
                print("\n完整回复内容:")
                print("-" * 50)
                print(full_content)
                print("-" * 50)
        
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
    asyncio.run(test_stream_chat())