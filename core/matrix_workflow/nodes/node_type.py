from enum import Enum

class NodeType(str, Enum):
    START = 'start'
    END = 'end'
    ADD = 'add'
    MINUS = 'minus'
    MULTIPLY = 'multiply'
    DIVIDE = 'divide'
    XHS = 'xhs'
    FACEBOOK = 'facebook'
