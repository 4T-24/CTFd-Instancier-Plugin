data = {}

def store(key, value):
    data[key] = value

def retrieve(key):
    return data.get(key)
