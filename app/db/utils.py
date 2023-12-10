import uuid


def create_id(length: int):
    num = str(uuid.uuid4().int >> (128 - 16))
    idx = list('0' * (length - len(num)))
    idx.extend(num)
    return ''.join(idx)

def create_id_len_five():
    return create_id(5)