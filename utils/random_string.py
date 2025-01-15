import string
from random import choices


def generate_random_string(length: int) -> str:
    return ''.join(choices(string.ascii_letters, k=length))