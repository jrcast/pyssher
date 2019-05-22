import argparse
import asyncio
import asyncssh
import logging
import signal
import sys

log_level = logging.DEBUG
server_command = 'while true; do echo $HOSTNAME && sleep 1; done'
servers = [{"hostname": "localhost",
            "port": 10000,
            "username": "root",
            "client_key": "id_rsa"},
           {"hostname": "localhost",
            "port": 10001,
            "username": "root",
            "client_key": "id_rsa"}]


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
#         print(data, end='')

    def connection_lost(self, exc):
        if exc:
            logging.error('SSH session error: ' + str(exc), file=sys.stderr)


class Pyssher():

    def __init__(self, clients):
        self.logger = logging.getLogger("pyssher")
        self.logger.setLevel(log_level)
        handler = logging.StreamHandler()
        self.logger.addHandler(handler)

        self.connections = []
        self.clients = clients
        #select which signals will be captured. These signals will be forwarded to remote clients once received
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

        self.logger.debug("Goodbye cruel world. I am now dead")
        sys.exit(exit_code)

    async def run_command_in_client(self, host, port, username, client_key, command):
        async with asyncssh.connect(host,
                                    port = port,
                                    username = username,
                                    client_keys = client_key,
    #                                 known_hosts = asyncssh.read_known_hosts("host_keys")) as conn:
                                    known_hosts = None) as conn:
            #         return await conn.create_session(MySSHClientSession, command)
            clientSession = MySSHClientSession("{}@{}:{}".format(username, host, port))
            chan, _session = await conn.create_session(clientSession, command)
            self.connections.append(conn)
            await chan.wait_closed()

    async def run_command_in_all_clients(self, command):
        sessions = [self.run_command_in_client(host=client["hostname"],
                                                    port=client["port"],
                                                    username=client["username"],
                                                    client_key=client["client_key"],
                                                    command=command) for client in self.clients]
        await asyncio.gather(*sessions, return_exceptions=True)


def pyssher():
    try:
        agent = Pyssher(servers)
        asyncio.get_event_loop().run_until_complete(agent.run_command_in_all_clients(server_command))
    except (OSError, asyncssh.Error) as exc:
        sys.exit('SSH connection failed: ' + str(exc))
