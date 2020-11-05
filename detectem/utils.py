import hashlib
import json
import pprint

from detectem.settings import CMD_OUTPUT, JSON_OUTPUT


def get_most_complete_pm(pms):
    """Return plugin match with longer version, if not available
    will return plugin match with ``presence=True``
    """
    if not pms:
        return None

    selected_version = None
    selected_presence = None

    for pm in pms:
        if pm.version:
            if not selected_version:
                selected_version = pm
            else:
                if len(pm.version) > len(selected_version.version):
                    selected_version = pm
        elif pm.presence:
            selected_presence = pm

    return selected_version or selected_presence


def create_printer(oformat):
    if oformat == CMD_OUTPUT:
        return pprint.pprint
    elif oformat == JSON_OUTPUT:

        def json_printer(data):
            print(json.dumps(data))

        return json_printer


def get_url(entry):
    """ Return URL from response if it was received otherwise requested URL. """
    try:
        return entry["response"]["url"]
    except KeyError:
        return entry["request"]["url"]


def get_response_body(entry):
    return entry["response"]["content"]["text"]


def get_version_via_file_hashes(plugin, entry):
    file_hashes = getattr(plugin, "file_hashes", {})
    if not file_hashes:
        return

    url = get_url(entry)
    body = get_response_body(entry).encode("utf-8")
    for file, hash_dict in file_hashes.items():
        if file not in url:
            continue

        m = hashlib.sha256()
        m.update(body)
        h = m.hexdigest()

        for version, version_hash in hash_dict.items():
            if h == version_hash:
                return version
