from tests import tree


def create_har_entry(yaml_dict, field):
    fake_har_entry = tree()

    if field == 'url':
        fake_har_entry['request']['url'] = yaml_dict['url']
        fake_har_entry['response']['url'] = yaml_dict['url']
    elif field == 'body':
        fake_har_entry['response']['content']['text'] = yaml_dict['body']
    elif field == 'header':
        fake_har_entry['response']['headers'] = [yaml_dict['header']]
    elif field == 'xpath':
        fake_har_entry['response']['content']['text'] = yaml_dict['xpath']

    return fake_har_entry
