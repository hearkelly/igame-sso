import hashlib
import os
import re

def hash_email(email) -> str:
    """
    :param:  input validated in form
    :return: salted, hashed input as string
    """
    salt = os.environ.get('SALT') or 'PLAYAGAME'
    email += salt
    hashed = hashlib.md5(email.encode())
    return hashed.hexdigest()

def validate_email(email) -> bool:
    try:
        name,domain = email.split('@',1)
    except:
        domain = None
    if domain:
        pattern = re.match(r'^[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*(\.[a-zA-Z]{2,63})',domain)
        if pattern:
            return True
    return False
