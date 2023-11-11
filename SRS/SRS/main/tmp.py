import random
import string
import uuid

# def func(length=10, existing_set=None):
#     characters = string.ascii_letters + string.digits
#     while True:
#         random_string = ''.join(random.choice(characters).upper() for _ in range(length))
#         if existing_set is None or random_string not in existing_set:
#             return random_string

def func():
    print(uuid.uuid4())

print(func())