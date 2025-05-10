from enum import Enum

class NodeType(str, Enum):
    START = 'start'
    END = 'end'
    IF_ELSE = 'if_else'
    HTTP_REQUEST = 'http_request'
    XHS = 'xhs'
    FACEBOOK = 'facebook'
    TIKTOK = 'tiktok'
    CODE = 'code'
