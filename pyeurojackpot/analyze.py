from helpers import log

import os
import sys

from lotto import Lotto

FOLDER = "database"
LOTTO_DATABASE = os.path.join(FOLDER, "lottoDB")
LOTTO_TIPS = os.path.join(FOLDER,"ordersDB")

if __name__ == "__main__":
    try:
        Lotto("Lotto Numbers: ver. 2021-06-02").execute(sys.argv, LOTTO_DATABASE, LOTTO_TIPS)
    except Exception as e:
        log(e,)
