import bcrypt


def hash_password(password: str) -> str:
    """
    对密码加密
    :param password: 用户输入的密码
    :return: 加密后的密码
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed_password: str) -> bool:
    """
    验证密码的有效性
    :param password: 用户输入的明文密码
    :param hashed_password: 数据库中的加密密码
    :return: 是否匹配
    """
    return bcrypt.checkpw(
        password.encode("utf-8"), hashed_password.encode("utf-8")
    )
