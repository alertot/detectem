def meta_generator(name):
    return '//meta[@name="generator" and contains(@content, "{}")]' \
            '/@content'.format(name)
