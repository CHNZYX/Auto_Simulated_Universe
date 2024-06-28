import argparse

from utils.diver.config import config
def str2bool(v):
    return v.lower() in ("true", "t", "1")
parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='Debug mode', default=False, action='store_true')
parser.add_argument('--nums', type=int, help='Num of excution', default=config.max_run)
parser.add_argument('--speed', help='Speed mode', default=False, action='store_true')
parser.add_argument('--cpu', help='Cpu mode', default=False, action='store_true')
args = parser.parse_args()