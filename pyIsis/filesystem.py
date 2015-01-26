
import platform
from subprocess import Popen, PIPE


def mount_workspace(server,workspacename,username,password,mountpoint):
    system = platform.system()
    if system == "Darwin":
        cmd_format = "/sbin/mount_AvidUnityISIS -U {username}:{password} {server}:{workspacename} {mountpoint}"
        print cmd_format
    elif system == "Linux":
        cmd_format = "/sbin/mount.avidfos {username}:{password}@{server}/{workspacename} {mountpoint}"
    else:
        cmd_format = ''

    cmd = cmd_format.format(server=server,
                            workspacename=workspacename,
                            username=username,
                            password=password,
                            mountpoint=mountpoint)
    process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    process.wait()

    code = process.returncode
    if code != 0:
        if code == 13:
            print "Username %s has no access to workspace %s." % \
                    (username, workspacename)
        if code == 3:
            print "Workspace %s does not exits or unreachable." % \
                    workspacename
        return False
    else:
        return True


def umount_workspace(mountpoint):
    system = platform.system()
    if system == "Darwin":
        cmd = "/sbin/umount {mountpoint}".format(mountpoint=mountpoint)
        process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        process.wait()
        code = process.returncode
        return code
    elif system == "Linux":
        cmd = "/sbin/umount {mountpoint}".format(mountpoint=mountpoint)
        process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        process.wait()
        code = process.returncode
        if code != 0:
            return False
        else:
            try:
                os.rmdir(mountpoint)
                return True
            except OSError as ex:
                if ex.errno == errno.ENOTEMPTY:
                    print "directory not empty"
                    return False
    else:
        pass


if __name__ == "__main__":
    mount_workspace(server="ISIS-ROUGE",
                    workspacename="ALC_Projets",
                    username="zSECU",
                    password="",
                    mountpoint="/Volumes/ALC_Projets")
