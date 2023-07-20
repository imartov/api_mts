import uuid


def create_extra_id() -> str:
    ''' generate random UUID fot extra_id '''
    return str(uuid.uuid4())


if __name__ == "__main__":
    create_extra_id()