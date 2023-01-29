import string
import unicodedata

from framework.lib.fut_cloud import FutCloud
from framework.server_handler import ServerHandlerClass

ExpectedShellResult = 0
SERVER_HANDLER_GLOBAL = ServerHandlerClass()
SERVER_HANDLER_GLOBAL.__setattr__('fut_cloud', FutCloud(server_handler=SERVER_HANDLER_GLOBAL))

established_connection_handlers_var = []

valid_filename_chars = f"-_.() {string.ascii_letters}{string.digits}"
char_limit = 200


def string_to_filename(
    input_string,
    whitelist=valid_filename_chars,
    replace_characters=' ',
    replace_with="_",
):
    for r in replace_characters:
        input_string = input_string.replace(r, replace_with)
    cleaned_filename = unicodedata.normalize('NFKD', input_string).encode('ASCII', 'ignore').decode()
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    return cleaned_filename[:char_limit]
