import os
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
python_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir, 'python27', '1.0'))

noarch_lib = os.path.abspath(os.path.join(python_path, 'lib', 'noarch'))
sys.path.append(noarch_lib)

root_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
data_path = os.path.abspath(os.path.join(root_path, os.pardir, os.pardir, 'data'))
data_xtunnel_path = os.path.join(data_path, 'x_tunnel')

lib_path = os.path.abspath(os.path.join(current_path, os.pardir, 'common'))
sys.path.append(lib_path)

ready = False
# don't remove, launcher web_control need it.


def create_data_path():
    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    if not os.path.isdir(data_xtunnel_path):
        os.mkdir(data_xtunnel_path)


create_data_path()

from xlog import getLogger

xlog = getLogger("x_tunnel")

import xconfig
from proxy_handler import Socks5Server
import global_var as g
import proxy_session
import simple_http_server
import front_dispatcher

import web_control
# don't remove, launcher web_control need it.


def xxnet_version():
    version_file = os.path.join(root_path, "version.txt")
    try:
        with open(version_file, "r") as fd:
            version = fd.read()
        return version
    except Exception as e:
        xlog.exception("xxnet_version fail")
    return "get_version_fail"


def load_config():
    if len(sys.argv) > 2 and sys.argv[1] == "-f":
        config_path = sys.argv[2]
    else:
        config_path = os.path.join(data_xtunnel_path, 'client.json')

    xlog.info("use config_path:%s", config_path)

    config = xconfig.Config(config_path)

    config.set_var("log_level", "DEBUG")
    config.set_var("write_log_file", 0)

    config.set_var("encrypt_data", 0)
    config.set_var("encrypt_password", "encrypt_pass")
    config.set_var("encrypt_method", "aes-256-cfb")

    config.set_var("api_server", "center.xx-net.net")
    config.set_var("server_host", "")
    config.set_var("server_port", 0)
    config.set_var("use_https", 1)
    config.set_var("port_range", 1)

    config.set_var("login_account", "")
    config.set_var("login_password", "")

    config.set_var("conn_life", 30)

    config.set_var("socks_host", "127.0.0.1")
    config.set_var("socks_port", 1080)

    # performance parameters
    # range 2 - 100
    config.set_var("concurent_thread_num", 50)

    # min roundtrip on road if connectoin exist
    config.set_var("min_on_road", 2)

    # range 1 - 1000, ms
    config.set_var("send_delay", 100)

    # range 1 - 20000, ms
    config.set_var("resend_timeout", 5000)

    # range 1 - resend_timeout, ms
    config.set_var("ack_delay", 300)

    # max 10M
    config.set_var("max_payload", 128 * 1024)

    # range 1 - 30
    config.set_var("roundtrip_timeout", 15)

    config.set_var("network_timeout", 10)

    config.set_var("windows_size", 16 * 1024 * 1024)

    config.load()

    config.windows_ack = 0.05 * config.windows_size
    xlog.info("X-Tunnel window:%d", config.windows_size)

    if config.write_log_file:
        xlog.log_to_file(os.path.join(data_path, "client.log"))

    xlog.setLevel(config.log_level)
    xlog.set_buffer(500)
    g.config = config


def start():
    g.running = True
    if not g.server_host or not g.server_port:
        if g.config.server_host and g.config.server_port:
            xlog.info("Session Server:%s:%d", g.config.server_host, g.config.server_port)
            g.server_host = g.config.server_host
            g.server_port = g.config.server_port
            g.balance = 99999999
        elif g.config.api_server:
            pass
        else:
            xlog.debug("please check x-tunnel server in config")

    g.http_client = front_dispatcher

    g.session = proxy_session.ProxySession()


def terminate():
    global ready
    g.running = False
    g.http_client.stop()

    if g.socks5_server:
        xlog.info("Close Socks5 server ")
        g.socks5_server.server_close()
        g.socks5_server.shutdown()
        g.socks5_server = None

    if g.session:
        xlog.info("Stopping session")
        g.session.stop()
        g.session = None
    ready = False


def main(args):
    global ready
    load_config()
    g.data_path = data_path

    xlog.info("xxnet_version:%s", xxnet_version())

    start()

    allow_remote = args.get("allow_remote", 0)
    if allow_remote:
        listen_ip = "0.0.0.0"
    else:
        listen_ip = g.config.socks_host

    g.socks5_server = simple_http_server.HTTPServer((listen_ip, g.config.socks_port), Socks5Server, logger=xlog)
    xlog.info("Socks5 server listen:%s:%d.", g.config.socks_host, g.config.socks_port)

    ready = True
    g.socks5_server.serve_forever()


if __name__ == '__main__':
    try:
        main({})
    except KeyboardInterrupt:
        terminate()
        import sys

        sys.exit()
