#!/usr/bin/env python3

from datetime import datetime
import os
import shutil




def move_log_file(day):
    shutil.copy(f"/usr/local/python-scripts/backup_config/parallel/log.txt", f"/mnt/backup_config/!log/log_{day}.txt")
    os.remove(f"/usr/local/python-scripts/backup_config/parallel/log.txt")







if __name__ == "__main__":

    today = datetime.now().date()
    today = str(today)


    try:
        move_log_file(today)

    except:
        pass
