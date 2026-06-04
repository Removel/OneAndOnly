"""
流式聊天功能使用示例

这个文件展示了如何使用新的流式聊天 API
"""

import requests
import json

def simple_stream_chat_example():
    """
    简单的流式聊天示例
    """
    url = "http://localhost:8000/api/chat-stream"
    
    payload = {
        "human_input": "你好，请介绍一下你自己",
        "session_id": 1,
        "clear_history": True
    }
    
    print("发送请求...")
    response = requests.post(url, json=payload, stream=True)
    
    if response.status_code == 200:
        print("开始接收流式响应:\n")
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                
                if decoded_line.startswith('event:'):
                    event_type = decoded_line[6:].strip()
                    print(f"事件: {event_type}")
                
                elif decoded_line.startswith('data:'):
                    data_str = decoded_line[5:].strip()
                    if data_str:
                        data = json.loads(data_str)
                        
                        if 'content' in data:
                            print(f"内容: {data['content']}", end='', flush=True)
                        
                        elif event_type == 'done':
                            print(f"\n\n完成！情绪: {data.get('emotion_vac', {})}")
                        
                        elif event_type == 'error':
                            print(f"\n错误: {data.get('message', '未知错误')}")
    else:
        print(f"请求失败: {response.status_code}")

def advanced_stream_chat_example():
    """
    高级流式聊天示例，包含更完整的事件处理
    """
    url = "http://localhost:8000/api/chat-stream"
    
    payload = {
        "human_input": "今天天气怎么样？",
        "session_id": 1,
        "clear_history": False
    }
    
    full_content = ""
    emotion_vac = {}
    retry_times = 0
    error_message = None
    
    print("发送请求...")
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
        print("开始接收流式响应:\n")
        print("="*60)
        
        current_event_type = None
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                
                if decoded_line.startswith('event:'):
                    current_event_type = decoded_line[6:].strip()
                
                elif decoded_line.startswith('data:'):
                    data_str = decoded_line[5:].strip()
                    if data_str and current_event_type:
                        data = json.loads(data_str)
                        
                        if current_event_type == 'token':
                            content = data.get('content', '')
                            full_content += content
                            print(content, end='', flush=True)
                        
                        elif current_event_type == 'done':
                            emotion_vac = data.get('emotion_vac', {})
                            retry_times = data.get('retry_times', 0)
                            print("\n" + "="*60)
                            print("对话完成！")
                            print(f"情绪VAC: {emotion_vac}")
                            print(f"重试次数: {retry_times}")
                            print("="*60)
                        
                        elif current_event_type == 'error':
                            error_message = data.get('message', '未知错误')
                            print(f"\n错误: {error_message}")
        
        print(f"\n完整内容长度: {len(full_content)}")
        
    else:
        print(f"请求失败: {response.status_code}")
        print(f"错误信息: {response.text}")

if __name__ == "__main__":
    print("选择示例:")
    print("1. 简单示例")
    print("2. 高级示例")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        simple_stream_chat_example()
    elif choice == "2":
        advanced_stream_chat_example()
    else:
        print("无效选择")