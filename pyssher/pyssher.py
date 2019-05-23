import argparse
import asyncio
import asyncssh
import logging
import os
import re
import signal
import sys

log_level = logging.INFO


class MySSHClientSession(asyncssh.SSHClientSession):

    def __init__(self, prefix=None):
        self.logger = logging.getLogger(prefix if prefix else "clientsession")
        logformat = logging.Formatter('{}%(message)s'.format(prefix + " - " if prefix else ""))
        if not len(self.logger.handlers):
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logformat)
            self.logger.addHandler(handler)
        self.logger.setLevel(log_level)

    def __call__(self):
        return self

    def data_received(self, data, datatype):
        self.logger.info(data.replace("\n", ""))

    def connection_lost(self, exc):
        if exc:
            logging.error('SSH session error: ' + str(exc), file=sys.stderr)


class Pyssher():
    '''
    @param clients: dictironary with the client information. {hostname:, port:, username:}
    '''

    def __init__(self, clients):
        self.logger = logging.getLogger("pyssher")
        self.logger.setLevel(log_level)
        logformat = logging.Formatter('%(levelname)-8s %(message)s')
        if not len(self.logger.handlers):
            handler = logging.StreamHandler()
            handler.setFormatter(logformat)
            self.logger.addHandler(handler)

        self.connections = []
        self.clients = clients
        self.signals_to_capture = {signal.SIGTERM: "TERM",
                                   signal.SIGINT: "INT"}
        for registered_signal in self.signals_to_capture:
            signal.signal(registered_signal, self.signal_handler)

    def signal_handler(self, sig, frame):
        exit_code = 0
        for conn in self.connections:
            try:
                conn.close()
                self.logger.info("Sent signal {} to {}".format(sig, conn))
            except:
                self.logger.error("Error sending signal {} to {}".format(sig, conn))
                exit_code = -1

        self.logger.info("Goodbye cruel world. me now dead")
        sys.exit(exit_code)

    async def run_command_in_client(self, host, port, username, command, client_keys):
        try:
            async with asyncssh.connect(host,
                                        port = port,
                                        username = username,
                                        client_keys = client_keys,
                                        #known_hosts = asyncssh.read_known_hosts("host_keys")) as conn:
                                        known_hosts = None) as conn:

                clientSession = MySSHClientSession("{}@{}:{}".format(username, host, port))
                chan, _session = await conn.create_session(clientSession, command)
                self.connections.append(conn)
                await chan.wait_closed()

        except Exception as e:
            self.logger.error("When attempting to connect to {}@{}:{} got: {}".format(username, host, port, e))

    async def run_command_in_all_clients(self, command, keypath):
        paths = [os.path.join(keypath, f) for f in os.listdir(keypath)]
        sessions = [self.run_command_in_client(host=client["hostname"],
                                               port=client["port"],
                                               username=client["username"],
                                               client_keys=paths,
                                               command=command) for client in self.clients]

        await asyncio.gather(*sessions, return_exceptions=True)


def pyssher():
    global log_level
    logger = logging.getLogger("main")
    logformat = logging.Formatter('%(levelname)-8s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(logformat)
    logger.addHandler(handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="enable debug mode")
    parser.add_argument("-s", "--server", dest="servers", action="append", nargs="*",
                        help="input each server in the following format user@hostname:port")
    parser.add_argument("-c", "--command", dest="command", help="Shell command you want to execute in given servers")
    parser.add_argument("-k", "--keypath", dest="keypath", default= "/pyssher/keys",
                        help="Path to the directory containing ssh keys to use. Defaults to /pyssher/keys")

    args = parser.parse_args()

    if args.debug:
        log_level = logging.DEBUG
    logger.setLevel(log_level)

    servers = []
    for server in args.servers:
        server = re.split("@|:", server[0])
        if len(server) < 2:
            logger.error("Need username@hostname given in this format")
            raise Exception()
        s = {"username": server[0],
             "hostname": server[1],
             "port": 22 if len(server) < 3 else int(server[2])}
        servers.append(s)
        logger.info("Connecting to {}".format(s))

    logger.info("pyssher started")
    try:
        agent = Pyssher(servers)
        asyncio.get_event_loop().run_until_complete(agent.run_command_in_all_clients(args.command, args.keypath))
    except Exception as exc:
        sys.exit('SSH connection failed: ' + str(exc))

if __name__ == '__main__':
    pyssher()
