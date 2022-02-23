DEFAULT_FILTER = ['self', 'cls']


def generate_payload(exclude=None, **kwargs):
    """
    Generate payload
    :param exclude:
    :param kwargs:
    :return: dict
    """
    if exclude is None:
        exclude = []
    data = dict()
    for key, value in kwargs.items():
        if key not in exclude + DEFAULT_FILTER and value is not None and not key.startswith('_'):
            if type(value) is list:
                for i, x in enumerate(value):
                    data[f"{''.join([key.split('_')[0].lower(), *map(str.title, key.split('_')[1:])])}[{i}]"] = x
            else:
                data[''.join([key.split('_')[0].lower(), *map(str.title, key.split('_')[1:])])] = value
    return data
