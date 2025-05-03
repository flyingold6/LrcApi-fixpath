import argparse
import json
import yaml
import logging
import os

logger = logging.getLogger(__name__)

# 启动参数解析器
parser = argparse.ArgumentParser(description="启动LRCAPI服务器")
# 添加一个 `--port` 参数，默认值28883
parser.add_argument('--port', type=int, default=28883, help='应用的运行端口，默认28883')
parser.add_argument('--auth', type=str, default='', help='用于验证Header.Authentication字段，建议纯ASCII字符')
parser.add_argument("--musicpath",type=str, default='',help='定义音乐文件夹起始路径，用于歌词提交，如果客户端提交的文件是相对路径，则添加此起始路径转换为完整路径')
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
parser.add_argument('--ip', type=str, default='*', help='服务器监听IP，默认*')
parser.add_argument('--token', type=str, default='', help='锂API接口的Token')
parser.add_argument('--ai-type', type=str, default='openai', help='AI类型，默认openai')
parser.add_argument('--ai-model', type=str, default='gpt-4o-mini', help='AI模型，默认gpt-4o-mini')
parser.add_argument('--ai-base-url', type=str, default='https://api.openai.com/v1', help='AI基础URL，默认https://api.openai.com/v1')
parser.add_argument('--ai-api-key', type=str, default='', help='AI API Key，默认空')
kw_args, unknown_args = parser.parse_known_args()
arg_auths: dict = {kw_args.auth: "rwd"} if kw_args.auth else None


# 按照次序筛选首个非Bool False（包括None, '', 0, []等）值；
# False, None, '', 0, []等值都会转化为None
def first(*args):
    """
    返回第一个非False值
    :param args:
    :return:
    """
    result = next(filter(lambda x: x, args), None)
    return result

DEFAULT_DATA = {
            "server": {
                "ip": "*",
                "port": 28883
            },
            "auth": "",
            "ai": {
                "type": "openai",
                "model": "gemini-2.0-flash",
                "base_url": "https://lrc.cx/v1",
                "api_key": ""
            },
            "musicpath": ""
}

class Args:
    def __init__(self, data=None, default_config=None):
        self.__data: dict = data
        self.__default: dict = default_config or {}
        self.version = "1.6.0"
        self.debug = kw_args.debug

    def __invert__(self):
        """
        JSON: config/config.json
        YAML: config/config.yaml

        default: YAML
        """
        # 1. 首先用默认值初始化
        self.__data = self.__default.copy()
        
        # 2. 加载配置文件，使用update而不是直接赋值
        for loader in (self.__load_json, self.__load_yaml):
            data = loader()
            if isinstance(data, dict):
                self.__data.update(data)
                break
        
        # 3. 加载环境变量
        self.__load_env()
        
        # 4. 最后加载命令行参数（最高优先级）
        self.__load_arg()

    @staticmethod
    def __load_json() -> dict|None:
        file_path = os.path.join(os.getcwd(), "config", "config.json")
        try:
            with open(file_path, "r+") as json_file:
                return json.load(json_file)
        # 解析错误
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    @staticmethod
    def __load_yaml() -> dict|None:
        file_path = os.path.join(os.getcwd(), "config", "config.yaml")
        try:
            with open(file_path, "r+") as yaml_file:
                return yaml.safe_load(yaml_file)
        except (yaml.YAMLError, FileNotFoundError):
            return None
        
    def __load_env(self):
        auth = os.environ.get('API_AUTH', None)
        port = os.environ.get('API_PORT', None)
        api_token = os.environ.get('API_TOKEN', None)
        ai_type = os.environ.get('API_AI_TYPE', None)
        ai_model = os.environ.get('API_AI_MODEL', None)
        ai_base_url = os.environ.get('API_AI_BASE', None)
        ai_api_key = os.environ.get('API_AI_KEY', None)
        if auth:
            self.__data["auth"] = auth
        if port:
            if not isinstance(self.__data.get("server"), dict):
                self.__data["server"] = {"ip": "*"}
            self.__data["server"]["port"] = port
        if api_token:
            self.__data["token"] = api_token
        if not isinstance(self.__data.get("ai"), dict):
            self.__data["ai"] = {}
        if ai_type:
            self.__data["ai"]["type"] = ai_type
        if ai_model:
            self.__data["ai"]["model"] = ai_model
        if ai_base_url:
            self.__data["ai"]["base_url"] = ai_base_url
        if ai_api_key:
            self.__data["ai"]["api_key"] = ai_api_key

    def __load_arg(self):
        auth = kw_args.auth
        port = kw_args.port
        musicpath = kw_args.musicpath
        ip = kw_args.ip
        token = kw_args.token
        ai_type = kw_args.ai_type
        ai_model = kw_args.ai_model
        ai_base_url = kw_args.ai_base_url
        ai_api_key = kw_args.ai_api_key
        if auth:
            self.__data["auth"] = auth
        if port:
            if not isinstance(self.__data.get("server"), dict):
                self.__data["server"] = {"ip": "*"}
            self.__data["server"]["port"] = port
        if musicpath:
            self.__data["musicpath"] = musicpath
        if ip:
            if not isinstance(self.__data.get("server"), dict):
                self.__data["server"] = {"ip": "*"}
            self.__data["server"]["ip"] = ip
        if token:
            self.__data["token"] = token
        if not isinstance(self.__data.get("ai"), dict):
            self.__data["ai"] = {}
        if ai_type:
            self.__data["ai"]["type"] = ai_type
        if ai_model:
            self.__data["ai"]["model"] = ai_model
        if ai_base_url:
            self.__data["ai"]["base_url"] = ai_base_url
        if ai_api_key:
            self.__data["ai"]["api_key"] = ai_api_key

    def __call__(self, *args):
        data = self.__data
        default = self.__default
        for key in args:
            if key in data:
                data = data[key]
            elif key in default:
                data = default[key]
            else:
                return None
        return data
    
args = Args(default_config=DEFAULT_DATA)
~args  # 初始化配置

if __name__ == '__main__':
    default: dict = {
        "server": {
            "ip": "*",
            "port": 28883
        },
        "auth": "",
        "token": "",
        "musicpath": ""
    }
    config = Args(default_config=default)
    ~config
    print(config("server", "port", "musicpath"))
