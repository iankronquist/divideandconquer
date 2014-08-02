from datetime import datetime

import redis


def get_corpus(out_file_prefix='corpus'):
    r_server = redis.Redis()
    out_file = open(out_file_prefix + str(datetime.now()) + '.json', 'w')
    length = r_server.llen('all')
    out_file.write('{{\n"count": "{}",\n"results": [\n'.format(length))
    for resp_id in r_server.lrange('all', 0, length - 1):
        jsonResp = r_server.get(resp_id)
        out_file.write(jsonResp + ",\n")
    # trailing comma
    for resp_id in r_server.lrange('all', length - 1, length):
        jsonResp = r_server.get(resp_id)
        out_file.write(jsonResp + "\n")
    out_file.write('\n]\n}')
    out_file.close()


if __name__ == '__main__':
    get_corpus()
