import hashlib 

def support_hash_file(data):
    '''Hashes the passed content using sha256'''
    return hashlib.sha256(data).hexdigest()