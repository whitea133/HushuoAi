import config as cfg
import hushuoGUI.shared as shared
from api_manager import multimodal_ordered
from hushuoGUI.shared import global_wx as wx

messages_record = [cfg.MODEL_ROLE]  # 初始化模型身份
# ---------- 生成回答 ----------
def generate_once():
    with shared.buffer_lock:
        if not shared.buffer_msgs:
            shared.reply_q.put("当前无消息可生成")
            return
        # 直接传已排序的 buffer_msgs
        shared.buffer_msgs.sort(key=lambda x: x["ts"])
        reply = multimodal_ordered(shared.buffer_msgs, messages_record)
        shared.reply_q.put(reply)
        
# ---------- 重新生成 ----------
def regenerate():
    generate_once()

# ---------- 发送回微信 ----------
def send_back_to_wechat():
    wx.SendMsg(shared.send_q.get(), who=shared.target_man)
    # 清空消息缓冲区
    shared.buffer_msgs.clear()