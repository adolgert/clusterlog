# Cluster Log

Andrew Dolgert, adolgert@uw.edu

This is a helper module to set up logging that sends
messages from remote clients to a single server.
You start a receiver program, included with the repository,
that listens for log messages. Then start many other programs,
on the same machine or other machines, which send log messages
to that receiver.

## On the client

There are two ways to use this. One is to ask it to add arguments to
the parser, and the other lets you pass in a logging level.

```python
import argparse
import clusterlog

logger = clusterlog.getLogger("package.file")

def function():
    logger.info("Entering function")

if __name__ = "__main__":
    parser = argparse.ArgumentParser(description = "Sample cluster program")
    clusterlog.add_argparse_options(parser)
    args = parser.parse_args()

    clusterlog.setup_from_parse_args(args)

    function()
```
This adds to command-line arguments -q for quiet, -v for verbose,
--trace for trace, and --loghost to specify where to send messages.
The loghost format is "host:port", with a default port of 5005.
This sample file
will have the following help:
```
adolgert@ithaca:~/dev/clusterlog$ python sample.py --help
usage: sample.py [-h] [--dontstop] [--loghost LOGHOST] [-q] [-v] [--trace]

Sample cluster program

optional arguments:
  -h, --help         show this help message and exit
  --loghost LOGHOST  Where to send logging messages
  -q                 quiet logging
  -v                 verbose logging
  --trace            trace logging
```

The direct way, with more control, is to just set your own logging level however
you would like.
```python
import logging
import clusterlog

logger = clusterlog.getLogger("package.file")

def function():
    logger.info("Entering function")

if __name__ = "__main__":
    logging.basicConfig(level=logging.DEBUG)
    clusterlog.add_handler(logging.root, logging.INFO, "listening_host", 5005)

    function()
```
## On the server
The listener will either print messages to stdout or to a file. It will either batch those
messages in memory before writing the batch to disk, or write them immediately.
Its arguments to be quiet, verbose, or trace indicate what level of messages
from clients it will print or ignore.
```
adolgert@ithaca:~$ loglisten --help
usage: loglisten [-h] [--listen LISTEN] [--out OUT] [--batches BATCHES]
                 [--loghost LOGHOST] [-q] [-v] [--trace]

This receives logging messages from clients.

optional arguments:
  -h, --help         show this help message and exit
  --listen LISTEN    The dotted decimal address and port on which to listen.
  --out OUT          The name of a file to which to write.
  --batches BATCHES  A buffer size if messages should be buffered
  -q                 quiet logging
  -v                 verbose logging
  --trace            trace logging
```
