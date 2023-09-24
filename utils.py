import uuid, os, json, re
from dotenv import load_dotenv


def create_extra_id() -> str:
    ''' generate random UUID fot extra_id '''
    return str(uuid.uuid4())


if __name__ == "__main__":
    pass
    
