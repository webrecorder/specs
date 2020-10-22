import hashlib 

def support_hash_file(data):
    '''Hashes the passed content using sha224'''
    hashlib.sha224(data).hexdigest()