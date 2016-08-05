import argparse
import itertools
import time
import clusterlog

# At the top of each Python file, create a local logger.
logger = clusterlog.getLogger("clusterlog.sample")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample cluster program")
    parser.add_argument("--dontstop", action="store_true",
                        help="Keep sending log messages forever")
    clusterlog.add_argparse_options(parser)
    args = parser.parse_args()

    clusterlog.setup_from_parse_args(args)
    logger.info("start {}".format(str(args.loghost)))

    if args.dontstop:
        beep_set=itertools.count()
    else:
        beep_set=range(30)

    for beep_step in beep_set:
        logger.log(1, "trace {}".format(beep_step))
        logger.debug("debug {}".format(beep_step))
        logger.info("info {}".format(beep_step))
        time.sleep(1)

    logger.info("finish")
    
