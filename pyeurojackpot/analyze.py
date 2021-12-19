import sys
from helpers import Lotto, log


LOTTO_DATABASE = "lottoDB"
LOTTO_TIPS = "ordersDB"

if __name__ == "__main__":
    try:
        Lotto("Lotto Numbers: ver. 2021-06-02").execute(sys.argv, LOTTO_DATABASE, LOTTO_TIPS)
    except Exception as e:
        log(e,)
