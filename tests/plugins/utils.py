from tests import tree


def create_har_entry(field, yaml_dict=None, value=None):
    fake_har_entry = tree()

    try:
        content = yaml_dict[field]
    except (TypeError, KeyError):
        content = value

    assert content

    if field == "url":
        fake_har_entry["request"]["url"] = content
        fake_har_entry["response"]["url"] = content
    elif field == "body":
        fake_har_entry["response"]["content"]["text"] = content
    elif field == "header":
        fake_har_entry["response"]["headers"] = [content]
    elif field == "xpath":
        fake_har_entry["response"]["content"]["text"] = content

    return fake_har_entry
