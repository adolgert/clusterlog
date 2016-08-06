# Cluster Log

Andrew Dolgert, adolgert@uw.edu

This is a helper module to set up logging that sends
messages from remote clients to a single server.
You start a receiver program, included with the repository,
that listens for log messages. Then start many other programs,
on the same machine or other machines, which send log messages
to that receiver.

There are two ways to use this. One is to ask it to add arguments to
the parser, and the other lets you pass in a logging level.

```python
import argparse
import clusterlog

logger = clusterlog.getLogger("package.file")

def function():
    logger.info("Entering function")

if __name__ = "__main__":
    parser = argparse.ArgumentParser(description = "This is my program")
    clusterlog.add_argparse_options(parser)
    args = parser.parse_args()

    clusterlog.setup_from_parse_args(args)

    function()
```
This adds to command-line arguments -q for quiet, -v for verbose,
--trace for trace, and --loghost to specify where to send messages.

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
