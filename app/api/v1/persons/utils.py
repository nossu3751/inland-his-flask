import datetime, json, base64
from flask import Response, Request

class Session():
    def __init__(self, token:dict, userinfo:dict, session_id:str):
        self.token = token
        self.userinfo = userinfo
        self.session_id = session_id

def get_expiry_string(expires_in:int) -> str:
    current_time_utc = datetime.datetime.utcnow()
    expiry_time_utc = current_time_utc + datetime.timedelta(seconds=expires_in)
    expiry_time_string = expiry_time_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    return expiry_time_string

def expired(expiry_time_string:str) -> bool:
    expiry_time_utc = datetime.datetime.strptime(expiry_time_string, "%Y-%m-%dT%H:%M:%SZ")
    current_time_utc = datetime.datetime.utcnow()
    return current_time_utc >= expiry_time_utc
   
def set_auth_cookie(res:Response, token:dict, userinfo:dict, session_id:str):
    
    
    token_type = token["token_type"]
    refresh_token = token["refresh_token"]
    access_token = token["access_token"]
    sub = userinfo["sub"]
    groups = userinfo["group_membership"]
    
    res.set_cookie("inland_his_token_type", token_type, httponly=True)
    res.set_cookie("inland_his_refresh_token", refresh_token, httponly=True)
    res.set_cookie("inland_his_access_token", access_token, httponly=True)
    res.set_cookie("inland_his_session_id", session_id, httponly=True)
    res.set_cookie("inland_his_sub", sub, httponly=True)
    res.set_cookie("inland_his_groups", str_from_dict(groups), httponly=True)

def remove_auth_cookie(res:Response):
    res.set_cookie("inland_his_token_type", "", expires=0)
    res.set_cookie("inland_his_refresh_token", "", expires=0)
    res.set_cookie("inland_his_access_token", "", expires=0)
    res.set_cookie("inland_his_sub", "", expires=0)
    res.set_cookie("inland_his_groups", "", expires=0)
    res.set_cookie("inland_his_session_id", "", expires=0)

def get_auth_cookie(req:Request) -> dict:
    cookies = req.cookies
    token_type_str = "inland_his_token_type"
    access_token_str = "inland_his_access_token"
    refresh_token_str = "inland_his_refresh_token"
    sub_str = "inland_his_sub"
    session_id_str = "inland_his_session_id"
    groups_str = "inland_his_groups"
    return {
        "token_type": cookies[token_type_str],
        "access_token": cookies[access_token_str],
        "refresh_token": cookies[refresh_token_str],
        "sub": cookies[sub_str],
        "session_id": cookies[session_id_str],
        "groups": cookies[groups_str]
    }
   
def str_from_dict(d) -> str:
    return json.dumps(d)

def dict_from_str(s:str) -> dict:
    return json.loads(s)

def binary_to_img(binary:str) -> str:
    base64_data = base64.b64encode(binary)
    return base64_data

def img_to_binary(base64str:str) -> str:
    binary_data = base64.b64decode(base64str)
    return binary_data

    
    