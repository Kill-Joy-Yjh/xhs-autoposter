"""
This example describes how to use the workflow interface to stream chat.
"""
import os
# Our official coze sdk for Python [cozepy](https://github.com/coze-dev/coze-py)
from cozepy import COZE_CN_BASE_URL

# Get an access_token through personal access token or oauth.
coze_api_token = 'pat_y15rSlKz60dy9OSCFeQva9xBJxcsNmVIKTSV67FMJed6UQAWDp6yChY4mMtG9Gkf'
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = COZE_CN_BASE_URL

from cozepy import Coze, TokenAuth, Stream, WorkflowEvent, WorkflowEventType  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

# Create a workflow instance in Coze, copy the last number from the web link as the workflow's ID.
workflow_id = '7522397995363713059'


# The stream interface will return an iterator of WorkflowEvent. Developers should iterate
# through this iterator to obtain WorkflowEvent and handle them separately according to
# the type of WorkflowEvent.
def handle_workflow_iterator(stream: Stream[WorkflowEvent]):
    import json
    import datetime
    import traceback
    def save_json_to_file(data, filename):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] 保存 {filename} 失败: {e}")

    def try_parse_json(content):
        try:
            return json.loads(content)
        except Exception:
            return None

    def get_timestamp():
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    interrupt_count = 0
    max_interrupt = 3

    for event in stream:
        try:
            if event.event == WorkflowEventType.MESSAGE:
                print("got message", event.message)
                msg = event.message
                # 兼容dict和str
                if isinstance(msg, dict) and "content" in msg:
                    content = msg["content"]
                else:
                    content = msg
                # 尝试解析content为json
                data = try_parse_json(content)
                if data and isinstance(data, dict):
                    for k, v in data.items():
                        # 保存每个字段到独立文件，带时间戳
                        save_json_to_file(v, f"coze_stream_{k}_{get_timestamp()}.json")
                # 也保存原始内容
                with open(f"coze_stream_raw_{get_timestamp()}.txt", "a", encoding="utf-8") as f:
                    f.write(f"got message {msg}\n")
            elif event.event == WorkflowEventType.ERROR:
                print("got error", event.error)
                with open(f"coze_stream_error_{get_timestamp()}.txt", "a", encoding="utf-8") as f:
                    f.write(f"got error {event.error}\n")
            elif event.event == WorkflowEventType.INTERRUPT:
                interrupt_count += 1
                print(f"[WARN] 收到中断事件，第{interrupt_count}次，event_id={event.interrupt.interrupt_data.event_id}")
                if interrupt_count > max_interrupt:
                    print("[ERROR] 中断次数过多，终止递归。")
                    break
                handle_workflow_iterator(
                    coze.workflows.runs.resume(
                        workflow_id=workflow_id,
                        event_id=event.interrupt.interrupt_data.event_id,
                        resume_data="hey",
                        interrupt_type=event.interrupt.interrupt_data.type,
                    )
                )
        except Exception as e:
            print(f"[EXCEPTION] 处理事件时出错: {e}\n{traceback.format_exc()}")
            with open(f"coze_stream_exception_{get_timestamp()}.txt", "a", encoding="utf-8") as f:
                f.write(f"Exception: {e}\n{traceback.format_exc()}\n")


if __name__ == "__main__":
    import sys
    user_input = None
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
    else:
        user_input = input("请输入对话内容：")
    handle_workflow_iterator(
        coze.workflows.runs.stream(
            workflow_id=workflow_id,
            parameters={
                "input": user_input
            }
        )
    )