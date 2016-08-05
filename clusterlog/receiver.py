'''
This is a service to listen for messages from processes
using the UDP logging handler, DatagramHandler. This listener is
meant to run on the head node of a parallel job so that it listens
for debugging messages from client tasks. It batches up the
messages and writes them to disk every so often. Call it in
the batch file with:

  python receiver.py&
  # Then start the client jobs with mpirun, or ibrun, or qsub, or whatever.
  pkill python

so that you kill it when the job is over. It will save events
before it quits.

The start of this code cema from the Python wiki,
wiki.python.org/moin/UdpCommunication.
'''

import argparse
import sys
import socket
import signal
import pickle
import logging
import logging.handlers
import clusterlog

logger=logging.getLogger("clusterlog.receiver")

# Using an empty UDP_IP, '', for the bind address mean we will accept
# messages from any host. To limit this to localhost, use
# UDP_IP='127.0.0.1'
UDP_IP=""
UDP_PORT=5005


def bind(host_ip, port):
    try:
        sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        sock.bind( (host_ip, port) )
    except socket.error as e:
        logger.exception(
                "Could not open network connection to listen {}".format(e))
        sys.exit()
    return sock



def store(sock, cluster_logger):
    while True:
        data, addr = sock.recvfrom( 8192 ) # buffer size
        try:
            pre_rec=pickle.loads(data[4:])
            rec = logging.makeLogRecord(pre_rec)
            logger.debug("Unpickled {}\n\tas a record {}".format(
                    str(pre_rec), str(rec)))
            logger.debug(cluster_logger.handlers)
            logger.debug("format {}".format(
                    cluster_logger.handlers[0].formatter._fmt))
            cluster_logger.handle(rec)
        except pickle.UnpicklingError as e:
            # This means it was a long record which we'll skip.
            logger.warn("Record could not be unpickled.")



class _OnExit(object):
    def __init__(self, handler, log):
        self.handler=handler
        self.log=log

    def __call__(self, signal, frame=None):
        if "flush" in dir(self.handler):
            self.handler.flush()
        if "close" in dir(self.log):
            self.log.close()
        sys.exit()



def loop_on_socket(out_file, log_level, batches):
    if out_file:
        stream_handler = logging.FileHandler(filename=out_file)
    else:
        stream_handler = logging.StreamHandler(stream=sys.stdout)

    formatter = logging.Formatter("SS%(asctime)s:%(name)s:%(levelname)s"
                                  ":%(tid)s:%(message)s")
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)

    if batches > 0:
        logger.debug("Handling logs in batches of {}".format(batches))
        batched_handler = logging.handlers.MemoryHandler(batches,
            log_level, stream_handler)
        formatter = logging.Formatter("BB%(asctime)s:%(name)s:%(levelname)s"
                                      ":%(tid)s:%(message)s")
        batched_handler.setFormatter(formatter)
        batched_handler.setLevel(log_level)
    else:
        batched_handler = stream_handler

    cluster_logger = logging.getLogger("clusterlog.receiver.network")
    # Disabling propagation means the root logger cannot receive
    # messages sent from the cluster.
    cluster_logger.propagate = False
    cluster_logger.addHandler(batched_handler)
    cluster_logger.setLevel(log_level)

    logger.info("Log level is {}".format(log_level))

    # We set up a signal handler because if someone hits ctrl-c on
    # this script, it will not have flushed logging messages to its
    # output yet. It's designed to hold them in memory.
    on_exit=_OnExit(stream_handler, batched_handler)
    signal.signal(signal.SIGTERM, on_exit)
    signal.signal(signal.SIGINT, on_exit)
    host, port=args.listen.split(":")
    store(bind(host, int(port)), cluster_logger)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="TOP %(message)s")
    parser = argparse.ArgumentParser(
        description="This receives logging messages from clients.")
    parser.add_argument("--listen", default="{}:{}".format(UDP_IP, UDP_PORT),
                        help="The dotted decimal address and port "
                             "on which to listen. " )
    parser.add_argument("--out",
                        help="The name of a file to which to write.")
    parser.add_argument("--batches", type=int, default=0,
                        help="A buffer size if messages should be buffered")
    clusterlog.add_argparse_options(parser)
    args = parser.parse_args()
    logger.debug("Arguments are {}".format(args))
    assert args.out is None or isinstance(args.out, str)
    assert isinstance(args.batches, int)
    assert args.batches >= 0

    log_level=clusterlog.verbosity_to_level(args)

    loop_on_socket(args.out, log_level, args.batches)
