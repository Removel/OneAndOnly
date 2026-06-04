"""
测试前端流式聊天功能的集成测试
"""
import asyncio
import json
import aiohttp

async def test_stream_chat():
    """测试流式聊天功能"""
    url = "http://localhost:8000/api/chat-stream"
    
    payload = {
        "human_input": "你好，请介绍一下你自己",
        "session_id": 1,
        "clear_history": True
    }
    
    print("开始测试流式聊天...")
    print(f"请求URL: {url}")
    print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                }
            ) as response:
                if response.status != 200:
                    print(f"请求失败，状态码: {response.status}")
                    return
                
                print("接收流式响应:")
                print("=" * 50)
                
                full_content = ""
                event_count = 0
                tool_calls = []
                node_events = []
                
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    
                    if line_str.startswith('event:'):
                        event_type = line_str[6:].strip()
                    
                    elif line_str.startswith('data:'):
                        data_str = line_str[5:].strip()
                        if data_str:
                            try:
                                data = json.loads(data_str)
                                event_count += 1
                                
                                if event_type == 'token' and 'content' in data:
                                    full_content += data['content']
                                    print(f"[Token] {data['content']}", end='', flush=True)
                                
                                elif event_type == 'tool_start':
                                    tool_info = {
                                        'tool': data.get('tool', 'unknown'),
                                        'input': data.get('input', ''),
                                        'status': 'started'
                                    }
                                    tool_calls.append(tool_info)
                                    print(f"\n[工具开始] {tool_info['tool']}: {tool_info['input'][:50]}...")
                                
                                elif event_type == 'tool_end':
                                    if tool_calls:
                                        tool_calls[-1]['status'] = 'completed'
                                        tool_calls[-1]['output'] = data.get('result', '')[:100]
                                    print(f"[工具结束] 结果: {data.get('result', '')[:50]}...")
                                
                                elif event_type == 'node_start':
                                    node_info = {'node': data.get('node', 'unknown'), 'status': 'started'}
                                    node_events.append(node_info)
                                    print(f"\n[节点开始] {node_info['node']}")
                                
                                elif event_type == 'node_end':
                                    if node_events:
                                        node_events[-1]['status'] = 'completed'
                                    print(f"[节点结束] {data.get('node', 'unknown')}")
                                
                                elif event_type == 'done':
                                    print(f"\n[完成] 状态: {data.get('status')}, 情绪VAC: {data.get('emotion_vac')}, 重试次数: {data.get('retry_times')}")
                                
                                elif event_type == 'error':
                                    print(f"\n[错误] {data.get('message', '未知错误')}")
                            
                            except json.JSONDecodeError as e:
                                print(f"\n解析JSON失败: {e}, 数据: {data_str}")
                
                print("\n" + "=" * 50)
                print(f"测试完成！共接收 {event_count} 个事件")
                print(f"完整内容长度: {len(full_content)} 字符")
                print(f"工具调用次数: {len(tool_calls)}")
                print(f"节点事件次数: {len(node_events)}")
                
                if tool_calls:
                    print("\n工具调用详情:")
                    for i, tool in enumerate(tool_calls, 1):
                        print(f"  {i}. {tool['tool']}: {tool['status']}")
                        if tool.get('input'):
                            print(f"     输入: {tool['input'][:100]}")
                        if tool.get('output'):
                            print(f"     输出: {tool['output'][:100]}")
                
                if node_events:
                    print("\n节点事件详情:")
                    for i, node in enumerate(node_events, 1):
                        print(f"  {i}. {node['node']}: {node['status']}")
                
    except aiohttp.ClientError as e:
        print(f"网络错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_stream_chat())