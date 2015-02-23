# -*- coding: utf-8 -*-

import os
import subprocess
import logging


#RSYNC_PATH = os.path.join(
#    os.path.abspath (os.path.dirname(__file__)), 'bin', 'rsync')
RSYNC_PATH = '/opt/rsync/bin/rsync'
RSYNC_CMD = '{cmd} {options} "{source}" "{destination}"'

rsync_logger = logging.getLogger('avidisis')


class rsync(object):
    """
    Run rsync as a subprocess sending output to a logger.
    This class subclasses subprocess.Popen
    """

    def __init__(self, src, dst, *options):
        self.src = src
        self.dst = dst
        self.options = options
        rsync_logger.debug('rsync parameters: {} {}'.format(src, dst))

    def run(self):
        cmd = RSYNC_CMD.format(
            cmd=RSYNC_PATH,
            options= ' '.join(self.options),
            source=self.src,
            destination=self.dst)

        process = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        output = ''
        # Poll process for new output until finished
        for line in iter(process.stdout.readline, ""):
            rsync_logger.debug('------ {}'.format(line.strip('\n\r')))
            #print '------ {}'.format(line.strip('\n\r'))
            output += line

        process.wait()
        exitCode = process.returncode

        if (exitCode == 0):
            rsync_logger.info('Workspace [{}] backup done.'.format(
                os.path.basename(self.src)))
            return output
        else:
            rsync_logger.error('rsync exitCode: {}, ouput {}'.format(
                exitCode, output))
            raise Exception(cmd, exitCode, output)


if __name__ == "__main__":
    r = rsync('/tmp/test/', '/tmp/test2', '-av', '--delete', '--exclude="*.log"')
    out = r.run()
    print out


