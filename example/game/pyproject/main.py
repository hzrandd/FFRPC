# -*- coding: utf-8 -*-
import ffext
import ff
import time
import msg_def.ttypes as msg_def
import random

MAX_X = 800
MAX_Y = 640
MOVE_SPEED = 3

g_move_offset = {
    "LEFT_ARROW":(-1, 0),
    "RIGHT_ARROW":(1, 0),
    "UP_ARROW":(0, -1),
    "DOWN_ARROW":(0, 1),
}
g_alloc_names = ['红', '明', '军', '兰', '猪', '楠', '微', '芳', '如', '熊', '牛', '兔', '七', '黄']

class player_t:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.x = 0
        self.y = 0
        self.last_move_tm = time.time()


@ffext.on_login(msg_def.client_cmd_e.LOGIN_REQ, msg_def.input_req_t)
def process_login(session, msg): #session_key,
    print('real_session_verify')
    session.verify_id(ffext.alloc_id())
    
    session.player = player_t()
    session.player.id = session.get_id()
    session.player.name = '小' + g_alloc_names[session.get_id() % (len(g_alloc_names))]
    session.player.x = 100 + random.randint(0, 100)
    session.player.y = 100 + random.randint(0, 100)
    
    ret_msg = msg_def.login_ret_t()
    ret_msg.id = session.get_id()
    ret_msg.x  = session.player.x
    ret_msg.y  = session.player.y
    ret_msg.name = session.player.name
    ret_msg.speed = MOVE_SPEED
    
    session.broadcast(msg_def.server_cmd_e.LOGIN_RET, ret_msg)
    print('real_session_enter', ret_msg)
    
    def notify(tmp_session):
        if tmp_session != session:
            ret_msg.id = tmp_session.get_id()
            ret_msg.x  = tmp_session.player.x
            ret_msg.y  = tmp_session.player.y
            ret_msg.name = tmp_session.player.name
            session.send_msg(msg_def.server_cmd_e.LOGIN_RET, ret_msg)
    ffext.get_session_mgr().foreach(notify)
    
    return []

@ffext.reg(msg_def.client_cmd_e.INPUT_REQ, msg_def.input_req_t)
def process_move(session, msg):
    print('process_move', msg.ops)
    now_tm = time.time()
    if now_tm - session.player.last_move_tm < 0.1:
        print('move too fast')
        return
    session.player.last_move_tm = now_tm
    offset = g_move_offset.get(msg.ops)
    if None == offset:
        return
    session.player.x += offset[0] * MOVE_SPEED
    session.player.y += offset[1] * MOVE_SPEED
    if session.player.x < 0:
        session.player.x = 0
    elif session.player.x > MAX_X:
        session.player.x = MAX_X
    if session.player.y < 0:
        session.player.y = 0
    elif session.player.y > MAX_Y:
        session.player.y = MAX_Y

    ret_msg     = msg_def.input_ret_t()
    ret_msg.id  = session.get_id()
    ret_msg.ops = msg.ops
    ret_msg.x   = session.player.x
    ret_msg.y   = session.player.y
    print('input', ret_msg)

    session.broadcast(msg_def.server_cmd_e.INPUT_RET, ret_msg)
    #ffext.change_session_scene(session.get_id(), 'scene@0')
    goto_msg = msg_def.input_req_t()
    goto_msg.ops = '%d_%d_%d'%(session.get_id(), session.player.x, session.player.y)
    session.goto_scene('scene@0', goto_msg)
    return

@ffext.on_logout
def process_logout(session):
    ret_msg = msg_def.logout_ret_t(session.get_id())
    session.broadcast(msg_def.server_cmd_e.LOGOUT_RET, ret_msg)
    print('process_logout', ret_msg, session.socket_id)

@ffext.on_enter(msg_def.input_req_t)
def process_enter(session, msg):
    session.player = player_t()
    param = msg.ops.split('_')
    session.player.id = int(param[0])
    session.verify_id(session.player.id)
    
    session.player.name = '小' + g_alloc_names[session.get_id() % (len(g_alloc_names))]
    session.player.x = int(param[1])
    session.player.y = int(param[2])
    
    print('process_enter', msg, session.socket_id)

def init():
    print('init......')
    ffext.set_protocol_type('json')
    return 0
    

def cleanup():
    print('cleanup.....')
    return 0