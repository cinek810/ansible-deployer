"""Module for handling infrastructure locks"""

import os
import sys
import pwd


class Locking:
    """Class handling infrastructure locks"""

    def __init__(self, logger, keep_lock, infra):
        self.logger = logger
        self.keep_lock = keep_lock
        self.infra = infra

    def lock_inventory(self, lockdir: str, lockpath: str):
        """
        Function responsible for locking inventory file.
        The goal is to prevent two parallel ansible-deploy's running on the same inventory
        This needs to be done by the use of additional directory under PARNT_WORKDIR,, for instance:
        PARENT_WORKDIR/locks.
        We shouldn't check if file exists, but rather attempt to open it for writing, until we're
        done every other process should be rejected this access.
        The file should match inventory file name.
        """

        self.logger.debug("Started lock_inventory for lockdir: %s and lockpath %s.", lockdir,
                          lockpath)
        os.makedirs(lockdir, exist_ok=True)

        try:
            with open(lockpath, "x", encoding="utf8") as fh:
                fh.write(str(os.getpid()))
                fh.write(str("\n"))
                fh.write(str(pwd.getpwuid(os.getuid()).pw_name))
            self.logger.info("Infra locked.")
        except FileExistsError:
            with open(lockpath, "r", encoding="utf8") as fh:
                proc_pid, proc_user = fh.readlines()
            self.logger.critical("Another process (PID: %s) started by user %s is using this"
                                " infrastructure, please try again later.", proc_pid.strip(),
                                proc_user.strip())
            sys.exit(61)
        except Exception as exc:
            self.logger.critical(exc)
            sys.exit(62)

    def unlock_inventory(self, lockpath: str):
        """
        Function responsible for unlocking inventory file, See also lock_inventory
        """

        self.logger.debug("Started unlock_inventory for lockpath %s.", lockpath)

        if not self.keep_lock:
            try:
                os.remove(lockpath)
                self.logger.info("Lock %s has been removed.", lockpath)
            except FileNotFoundError:
                self.logger.critical("Requested lock %s was not found. Nothing to do.", lockpath)
                sys.exit(63)
            except Exception as exc:
                self.logger.critical(exc)
                sys.exit(64)
        else:
            self.logger.debug("Keep locked infra %s:%s .", self.infra[0], self.infra[1])
