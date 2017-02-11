import logging
import ConfigParser
import os
import sys


CONFIG_FILENAME = 'conf/temp.conf'
EXIT_SUCCESS = 0

# Gets the value for a given key 'keyname' from the properties file 'filepath'
def get_property(keyname, section):
    cp = ConfigParser.ConfigParser()
    cp.read(CONFIG_FILENAME)
    try:
        return cp.get(section, keyname)
    except ConfigParser.NoOptionError:
        logging.error("Option %s not found in configuration file: %s Quitting..." % (keyname, CONFIG_FILENAME))
        report_failed_and_exit("Requested Config not found in file: " + CONFIG_FILENAME)

# Sets up logger with the configured log file
def setup_logger(logfile=None, verbose=None, console=None):
    if logfile is None:
        logfile = get_property('LOG_DIR', 'LOGS') + get_property('LOG_FILE', 'LOGS')
    if verbose is None:
        verbose = get_property('VERBOSE_LOGS', 'LOGS')
    if console is None:
        console = get_property('CONSOLE_LOGS', 'LOGS')

    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.getLogger('').handlers = []
    logging.basicConfig(level=log_level,
                        format='TempMon~[%(levelname)s] %(asctime)s, %(message)s',
                        datefmt='%Y-%m-%d-%H:%M:%S',
                        filename=logfile,
                        filemode='w+')
    if console:
        console = logging.StreamHandler()
        formatter = logging.Formatter('TempMon~[%(levelname)s] %(asctime)s, %(message)s', '%Y-%m-%d-%H:%M:%S')
        console.setFormatter(formatter)
        console.setLevel(log_level)
        logging.getLogger('').addHandler(console)

#check if reporting directory exists
def device_exists():
    return os.path.exists(get_property('DEVICES_DIR', 'SENSOR') + get_property('DEVICE_NAME', 'SENSOR'))

def report_dir_exists():
    return os.path.exists(get_property('REPORT_DIR', 'CONFIG'))

#checks for required files and fails out if not found
def check_files():
    if not os.path.exists(CONFIG_FILENAME):
        report_failed_and_exit('config file %s not found.' % CONFIG_FILENAME)

    data_dir = get_property('REPORT_DIR', 'CONFIG')
    if not report_dir_exists():
        try:
            os.makedirs(data_dir)
        except OSError:
            logging.error('Unable to create reporting directory. Check location of REPORT_DIR')
            report_failed_and_exit('Unable to create reporting directory')

# Reports setup failure and exits the program with error status
def report_failed_and_exit(message=None):
    if not message:
        message = 'Data collection terminated by error.'
    logging.error('FAILED: %s' % message)
    sys.exit(1)

def report_success_and_exit(message=None):
    if not message:
        message = 'Data collection finished.'
    logging.info('SUCCESS: %s' % message)
    sys.exit(0)

#create pretty title in log
def log_title(title):
    LINE_WIDTH = int(get_property('LINE_WIDTH', 'LOGS'))

    border_len = (LINE_WIDTH - len(title) - 4) / 2
    border = '|'
    for i in range(border_len):
        border += '-'
    border += ' ' + title + ' '
    if len(title) % 2 != 0:
        border += '-'
    for i in range(border_len):
        border += '-'
    border += '|'
    logging.info(border)