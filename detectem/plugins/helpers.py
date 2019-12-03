def meta_generator(name):
    return (
        '//meta[re:test(@name,"generator","i") and contains(@content, "{}")]'
        "/@content".format(name)
    )
