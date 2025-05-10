from enum import Enum, auto


class OperateEnums(Enum):
    # 0 发布
    # 1 评论
    # 2 点赞
    # 3 关注
    # 4 采集
    # 5 搜索
    POST = 0
    REPLY = auto()
    LIKE = auto()
    FOLLOW = auto()
    COLLECT = auto()
    REPOST = auto()
    SEARCH = auto()

    @classmethod
    def from_str(cls, value: int):
        """根据字符串值获取枚举成员"""
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"{value} is not a valid HeartOperate value")