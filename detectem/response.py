import base64
import json
import logging
import re
import urllib.parse

from string import Template

import pkg_resources
import requests

from detectem.exceptions import SplashError
from detectem.settings import SPLASH_TIMEOUT, SPLASH_URL
from detectem.utils import docker_container

DEFAULT_CHARSET = "iso-8859-1"
ERROR_STATUS_CODES = [400, 504]

logger = logging.getLogger("detectem")


def is_url_allowed(url):
    """ Return ``True`` if ``url`` is not in ``blacklist``.

    :rtype: bool

    """
    blacklist = [
        r"\.ttf",
        r"\.woff",
        r"fonts\.googleapis\.com",
        r"\.png",
        r"\.jpe?g",
        r"\.gif",
        r"\.svg",
    ]

    for ft in blacklist:
        if re.search(ft, url):
            return False

    return True


def is_valid_mimetype(response):
    """ Return ``True`` if the mimetype is not blacklisted.

    :rtype: bool

    """
    blacklist = ["image/"]

    mimetype = response.get("mimeType")
    if not mimetype:
        return True

    for bw in blacklist:
        if bw in mimetype:
            return False

    return True


def get_charset(response):
    """ Return charset from ``response`` or default charset.

    :rtype: str

    """
    # Set default charset
    charset = DEFAULT_CHARSET

    m = re.findall(r";charset=(.*)", response.get("mimeType", ""))
    if m:
        charset = m[0]

    return charset


def create_lua_script(plugins):
    """ Return script template filled up with plugin javascript data.

    :rtype: str

    """
    lua_template = pkg_resources.resource_string("detectem", "script.lua")
    template = Template(lua_template.decode("utf-8"))

    javascript_data = to_javascript_data(plugins)

    return template.substitute(js_data=json.dumps(javascript_data))


def to_javascript_data(plugins):
    """
    Return a dictionary with all JavaScript matchers. Quotes are escaped.

    :rtype: dict

    """

    def escape(v):
        return re.sub(r'"', r'\\"', v)

    def dom_matchers(p):
        dom_matchers = p.get_matchers("dom")
        escaped_dom_matchers = []

        for dm in dom_matchers:
            check_statement, version_statement = dm

            escaped_dom_matchers.append(
                {
                    "check_statement": escape(check_statement),
                    # Escape '' and not None
                    "version_statement": escape(version_statement or ""),
                }
            )

        return escaped_dom_matchers

    return [
        {"name": p.name, "matchers": dom_matchers(p)}
        for p in plugins.with_dom_matchers()
    ]


def get_response(url, plugins, timeout=SPLASH_TIMEOUT):
    """
    Return response with HAR, inline scritps and software detected by JS matchers.

    :rtype: dict

    """
    lua_script = create_lua_script(plugins)
    lua = urllib.parse.quote_plus(lua_script)
    page_url = f"{SPLASH_URL}/execute?url={url}&timeout={timeout}&lua_source={lua}"

    try:
        with docker_container():
            logger.debug("[+] Sending request to Splash instance")
            res = requests.get(page_url)
    except requests.exceptions.ConnectionError:
        raise SplashError("Could not connect to Splash server {}".format(SPLASH_URL))

    logger.debug("[+] Response received")

    json_data = res.json()

    if res.status_code in ERROR_STATUS_CODES:
        raise SplashError(get_splash_error(json_data))

    softwares = json_data["softwares"]
    scripts = json_data["scripts"].values()
    har = get_valid_har(json_data["har"])

    js_error = get_evaljs_error(json_data)
    if js_error:
        logger.debug("[+] WARNING: failed to eval JS matchers: %(n)s", {"n": js_error})
    else:
        logger.debug("[+] Detected %(n)d softwares from the DOM", {"n": len(softwares)})
    logger.debug("[+] Detected %(n)d scripts from the DOM", {"n": len(scripts)})
    logger.debug("[+] Final HAR has %(n)d valid entries", {"n": len(har)})

    return {"har": har, "scripts": scripts, "softwares": softwares}


def get_splash_error(json_data):
    msg = json_data["description"]
    if "info" in json_data and "error" in json_data["info"]:
        error = json_data["info"]["error"]
        if error.startswith("http"):
            msg = "Request to site failed with error code {0}".format(error)
        elif error.startswith("network"):
            # see http://doc.qt.io/qt-5/qnetworkreply.html
            qt_errors = {
                "network1": "ConnectionRefusedError",
                "network2": "RemoteHostClosedError",
                "network3": "HostNotFoundError",
                "network4": "TimeoutError",
                "network5": "OperationCanceledError",
                "network6": "SslHandshakeFailedError",
            }
            error = qt_errors.get(error, "error code {0}".format(error))
            msg = "Request to site failed with {0}".format(error)
        else:
            msg = "{0}: {1}".format(msg, error)
    return msg


def get_evaljs_error(json_data):
    error = None
    if "errors" in json_data and "evaljs" in json_data["errors"]:
        res = json_data["errors"]["evaljs"]
        if isinstance(res, str):
            m = re.search(r"'message': '(.*?)'[,}]", res)
            if m:
                error = bytes(m.group(1), "utf-8").decode("unicode_escape")
    return error


def get_valid_har(har_data):
    """ Return list of valid HAR entries.

    :rtype: list

    """
    new_entries = []
    entries = har_data.get("log", {}).get("entries", [])
    logger.debug("[+] Detected %(n)d entries in HAR", {"n": len(entries)})

    for entry in entries:
        url = entry["request"]["url"]
        if not is_url_allowed(url):
            continue

        response = entry["response"]["content"]
        if not is_valid_mimetype(response):
            continue

        if response.get("text"):
            charset = get_charset(response)
            response["text"] = base64.b64decode(response["text"]).decode(charset)
        else:
            response["text"] = ""

        new_entries.append(entry)

        logger.debug("[+] Added URL: %(url)s ...", {"url": url[:100]})

    return new_entries
