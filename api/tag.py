import os
import json
import logging

from . import *

from flask import request

from mod import tag
from mod.auth import require_auth_decorator

logger = logging.getLogger(__name__)

from mod.args import args

@app.route('/tag', methods=['POST', 'PUT'], endpoint='set_tag_endpoint')
@app.route('/confirm', methods=['POST', 'PUT'], endpoint='set_tag_endpoint')
@require_auth_decorator(permission='rw')
def set_tag():
    try:
        music_data_json: str = request.data.decode('utf-8')
        music_data: dict = json.loads(music_data_json)
    except json.JSONDecodeError:
        return "Invalid JSON.", 422
    except UnicodeError:
        return "Invalid encoding.", 422
    audio_path: str = music_data.get("path")
    audio_path_first: str = audio_path[0] if audio_path else ""
    if audio_path_first != "/" and audio_path_first != "":
        audio_path = args("musicpath") + "/" + audio_path
    if not audio_path:
        return "Missing 'path' key in JSON.", 422
    logger.debug(f"Editing file {audio_path}")
    if not os.path.exists(audio_path):
        logger.error(f"File not found: {audio_path}")
        return "File not found.", 404
    supported_tags = {
        "tracktitle": {"allow": (str, bool, type(None)), "caption": "Track Title"},
        "artist": {"allow": (str, bool, type(None)), "caption": "Artists"},
        "album": {"allow": (str, bool, type(None)), "caption": "Albums"},
        "year": {"allow": (int, bool, type(None)), "caption": "Album year"},
        "lyrics": {"allow": (str, bool, type(None)), "caption": "Lyrics text"}
    }
    music_data["tracktitle"] = music_data.get("tracktitle") or music_data.get("title")
    tags_to_set = {}
    for key, value in music_data.items():
        if key in supported_tags and isinstance(value, supported_tags[key]["allow"]):
            tags_to_set[key] = value
    try:
        tag.write(tags=tags_to_set, file=audio_path)
    except TypeError as e:
        logger.error(f"TypeError at endpoint /confirm: {str(e)}")
        return {"code": 524, "error": str(e)}, 524
    except FileNotFoundError as e:
        logger.error(f"Error at endpoint /confirm: {audio_path} file not found.")
        return {"code": 404, "error": str(e)}, 404
    except Exception as e:
        logger.error(f"Unknown Error at endpoint /confirm: {str(e)}")
        return {"code": 500, "error": str(e)}, 500
    return {"code": 200, "log": f"Successfully edited file {audio_path}"}, 200
