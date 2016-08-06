'''
This module enables logging from a client to a server
using the DatagramHandler.
'''
import logging
import logging.handlers
import os
import socket
import types

logger = logging.getLogger("clusterlog.clusterlog")



def add_argparse_options(parser):
    """
    This adds flags for quiet, verbose, and trace settings for logging.
    It also adds an option --loghost, for where to send logging messages.
    """
    parser.add_argument("--loghost",
                        help="Where to send logging messages")
    parser.add_argument("-q", action="store_true", help="quiet logging")
    parser.add_argument("-v", action="store_true", help="verbose logging")
    parser.add_argument("--trace", action="store_true", help="trace logging")



def verbosity_to_level(parsed_args):
    """
    Given arguments for quiet, verbose, and trace, returns a logging level.
    It assumes the command line arguments were -q, -v, and --trace.
    
    :param parse(args): The parsed argument list from argparse
    :returns: an integer logging level
    """
    def choose_and_return(args, log_levels):
        logger.debug("args {} levels {}".format(args, log_levels))
        if args[0]:
            return log_levels[0]
        else:
            return choose_and_return(args[1:], log_levels[1:])

    # We include the "trace" option to catch all low-level logging.
    # Trace is 1 because 0 means "not set".
    return choose_and_return(
        [parsed_args.trace, parsed_args.v, parsed_args.q, True],
        [1, logging.DEBUG, logging.WARNING, logging.INFO]
        )



def setup_from_parse_args(parse_args):
    """
    Given the parsed arguments from an argparse, this initializes logging.
    It assumes the command line arguments were --loghost, -q, -v, and --trace.

    :param parse(args): The parsed argument list from argparse.
    :returns: None
    """
    chosen_level=verbosity_to_level(parse_args)
    if parse_args.loghost:
        host_port=parse_args.loghost.split(":")
        if len(host_port)>1:
            add_handler(logging.root, chosen_level,
                        host_port[0], int(host_port[1]))
        else:
            add_handler(logging.root, chosen_level, host_port[0])
    else:
        logging.basicConfig(level=chosen_level, format=cluster_format())



def cluster_format():
    return "%(asctime)s:%(name)s:%(levelname)s:%(tid)s:%(message)s"


def add_handler(client_logger, userlevel, loghost, port=5005):
    """
    This adds to any logger, such as the root logger from logging.root,
    a handler which sends messages over a DatagramHandler to a host.

    :param userlevel: This is an integer logging level, such as logging.INFO.
    :param loghost: This is the cn name or ip address of a host that listens.
    """
    assert isinstance(client_logger, logging.Logger)
    assert isinstance(userlevel, int)
    assert isinstance(loghost, str)
    assert isinstance(port, int)

    handler = logging.handlers.DatagramHandler(loghost, port)
    handler.setLevel(userlevel)
    formatter = logging.Formatter(cluster_format())

    handler.setFormatter(formatter)
    client_logger.addHandler(handler)
    client_logger.setLevel(userlevel)



def getLogger(name):
    """
    This creates a logger to use as a logging class.
    You call this with log.info("message"), log.debug("message"), or the like.
    The dotted name is hierarchical and is usually named overall_module.file.
    This also adds a trace method to the logger. It just calls
    log() with a level of 5, as in logger.log(5, message).

    :param str name: This is a dotted name for the logger.
    :returns: An instance of a logger class.
    """
    if "HOSTNAME" in os.environ:
        unique_name = [os.environ["HOSTNAME"].split(".")[0]]
    else:
        unique_name = [socket.gethostname()]
    if "JOB_ID" in os.environ:
        unique_name.append(os.environ["JOB_ID"])
    else:
        pass # not job id. Fine.
    if "SGE_TASK_ID" in os.environ:
        unique_name.append(os.environ["SGE_TASK_ID"])
    else:
        pass # no task id. Fine.

    add_task_id=logging.LoggerAdapter(logging.getLogger(name),
        { "tid" : "-".join(unique_name) })
    def trace(self, message):
        self.log(5, message)
    add_task_id.trace=types.MethodType( trace, add_task_id )
    return add_task_id
