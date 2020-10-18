import hashlib 

def support_hash_file(data):
    '''Hashes the passed content using md5'''
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()