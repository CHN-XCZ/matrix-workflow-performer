from enum import Enum

class NodeType(str, Enum):
    START = 'start'
    END = 'end'
    IF_ELSE = 'if_else'
    XHS = 'xhs'
    FACEBOOK = 'facebook'
