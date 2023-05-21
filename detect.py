# --- Open cmt line bellow if run by cmd: python *.py
import sys  # nopep8
sys.path.append(".")  # nopep8
# ----
import os
import pyinotify

import subprocess
import shlex
import sys
import logging
import os
import os.path as op
import traceback
import datetime


import sentry_sdk  # nopep8
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN)
    sentry_sdk.capture_message(f"--- images_to_lp: Start 👍 ---")

PATH_VIDEOS = "/webapps/data/videos"
PATH_FRAMES = "/webapps/data/frames"
PATH_IMAGES = "/webapps/data/images"
PATH_WARNING = "/webapps/data/warning"

logger = logging.getLogger(sys.argv[0])
logSetup = False

ALLOWED_EXTENSIONS = set(['jpg', 'png'])


def exec_cmd(cmd, logger=logger):  # execute a shell command and return/print its output
    print(f"cmd is: {cmd}")
    logger.info("START [%s] : %s " % (datetime.datetime.now(), cmd))
    args = shlex.split(cmd)  # tokenize args
    output = None
    try:
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except Exception as e:
        ret = "ERROR   [%s] An exception occurred\n%s\n%s" % (
            datetime.datetime.now(), output, str(e))
        logger.error(ret)
        raise e  # todo ?
    ret = "END   [%s]\n%s" % (datetime.datetime.now(), output)
    # logger.info(ret)
    sys.stdout.flush()
    return output


class OnWriteHandler(pyinotify.ProcessEvent):
    def process_evt(self, event):
        """
        Ex: path = "/webapps/data/frames/vinwash/bigc_nga3vungtau/20230508/20230508T031021_001.jpg"

        Input:  "/webapps/data/frames/vinwash/bigc_nga3vungtau/20230508/20230508T031021_001.jpg"
        Output: "/webapps/data/images/vinwash/bigc_nga3vungtau/20230508/20230508T031021_001.jpg"
        """
        evt_path = str(event.pathname)
        print(evt_path)
        if len(evt_path.rsplit('.', 1)) == 1:
            return False

        if evt_path.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
            return False

        try:
            print(f"- Start process frames to lp: {evt_path}")
            evt_basename = op.basename(evt_path)
            (vod_name, _) = evt_basename.split("_")
            (vod_date, _) = vod_name.split("T")

            store_path = evt_path.replace(
                f"{PATH_FRAMES}/", ""
            ).replace(f"/{evt_basename}", "")
            print(f"--- store_path: {store_path}")

            images_path = f"{PATH_IMAGES}/{store_path}"
            if not op.exists(images_path):
                os.system(f"mkdir -p {images_path}")

            # Start Recognize
            recognize_license_number(evt_path, vod_name)
            print(f"--- recognize_license_number: Success")

            # Move Image to backup Folder
            os.system(f"mv {evt_path} {images_path}")
            print(f"--- Move Backup image: {images_path}/{evt_basename}")

            print(f"---x success x--- {evt_path}")

            return True
        except Exception as error:
            traceback.print_exc()
            return False

    def process_IN_CLOSE_WRITE(self, event):
        print(("process_IN_CLOSE_WRITE: " + event.pathname))
        return self.process_evt(event)

    def process_IN_MOVED_TO(self, event):
        print(("process_IN_MOVED_TO: " + event.pathname))
        return self.process_evt(event)

    def process_IN_DELETE(self, event):
        print(("Deleted file: " + event.pathname))


def auto_notify(path):
    # Set up notify event
    wm = pyinotify.WatchManager()
    handler = OnWriteHandler()
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    mask_monitor = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_DELETE | pyinotify.IN_MOVED_TO
    wm.add_watch(path, mask_monitor, rec=True, auto_add=True)
    print(('==> Start monitoring %s (type c^c to exit)' % (path)))
    notifier.loop()


if __name__ == '__main__':
    # print("- load new code #1")
    # auto_notify(PATH_FRAMES)
    exec_cmd("pwd")
