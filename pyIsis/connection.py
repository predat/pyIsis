# -*- coding: utf-8 -*-

import sys
import copy
import osa
import urllib
import urllib2
import xmltodict


ISIS_AGENT = '12345'
ISIS_SOAP_URL = 'http://{hostname}:{port}/?wsdl'
ISIS_SOAP_PORT = 80

ISIS_USER_READ = 1
ISIS_USER_WRITE = 3
ISIS_USER_NONE = 0


class LoginError(Exception):
    pass

class HostnameError(Exception):
    pass


class Client(object):
    """ A Class to management Avid Isis Storage from python.

        :Example:

        >>> from pyIsis import Client
        >>> client = Client(hostname="servername",
                            username="Administrator",
                            password="thepassword")
        >>> client.get_workspaces()
    """

    def __init__(self, hostname, username, password):
        """
            :param hostname: hostname or ip of the Avid Isis Storage server
            :param username: a valid username
            :param password: password of the user
        """
        self.hostname = hostname
        self.username = username
        self.password = password

        url = ISIS_SOAP_URL.format(hostname=self.hostname,
                                   port=ISIS_SOAP_PORT)

        try:
            self._client = osa.Client(url)
        except urllib2.URLError:
            raise HostnameError("Hostname %s not found." % self.hostname)

        try:
            self.token = self._client.service.Login(ISIS_AGENT,
                                                self.username,
                                                self.password)
        except ValueError:
            raise LoginError("Username or password invalid.")

        self.set_byte_count_divisor(1024*1024)

    def __del__(self):
        if self.token:
            self._client.service.Logout(self.token)

    def get_byte_count_divisor(self):
        return self._client.service.GetByteCountDivisor(self.token)

    def set_byte_count_divisor(self, byteCnt):
        """ Set byte divisor for all return capacity values """
        return self._client.service.SetByteCountDivisor(self.token, str(byteCnt))

    def get_users(self):
        """
            :return: list of all users in Avid Isis Storage
            :rtype: list
        """
        return self._client.service.GetUsers(self.token).users.user

    def get_user(self, name):
        """
            :return: user informations
            :rtype: osa.xmltypes.UserSummary (dict)
        """
        users = self.get_users()
        for user in users:
            if name in user.ioName:
                return user
        return None

    def get_user_details(self, name):
        """
            :return: user details (Workspace access and group membership)
            :rtype: osa.xmltypes.UserDetails (dict)
        """
        user = self.get_user(name)
        if user:
            return self._client.service.GetUserDetails(self.token, user.outID)
        else:
            return None

    def get_user_perm(self, username, workspace):
        user = self.get_user_details(username)
        if user:
            for acc in user.workspaceAccesses.access:
                if workspace in acc['outName']:
                    return int(acc['ioAccess'])
        return None

    def create_user(self, name):
        if not self.get_user(name):
            base = self._client.service.GetUserDetails(self.token, 'Create')
            user = copy.copy(base)
            user.ioName = name
            return self._client.service.ModifyUserDetails(self.token,
                                                          base, user)
        else:
            return None

    def delete_user(self, name):
        user = self.get_user(name)
        if user:
            user_wrapper = self._client.types.UsersWrapper(deep=True)
            user_wrapper.users.user = [user]
            return self._client.service.DeleteUsers(self.token, user_wrapper)
        else:
            return None

    def change_user_perm(self, username, workspace, permissions=ISIS_USER_NONE):
        user = self.get_user_details(username)
        if user:
            modify_user = copy.deepcopy(user)
            modify_user.userGroupMemberships.userGroupMembership = []
            user.userGroupMemberships.userGroupMembership = []
            for acc in user.workspaceAccesses.access:
                if acc.outName == workspace:
                    user.workspaceAccesses.access = [acc]
                    break

            workspace_to_add = self.get_workspace(workspace)
            if workspace_to_add:
                wp_access = self._client.types.WorkspaceAccess(deep=True)
                wp_access.outID = workspace_to_add.outID
                wp_access.outName = workspace_to_add.ioName
                wp_access.ioAccess = permissions
                modify_user.workspaceAccesses.access = [wp_access]
                return self._client.service.ModifyUserDetails(self.token,
                                                          user, modify_user)
            else:
                return None
        else:
            return None

    def get_groups(self):
        return self._client.service.GetUserGroups(self.token).usergroups.user

    def get_group(self, name):
        groups = self.get_groups()
        for group in groups:
            if name in group.ioName:
                return group
        return None

    def get_group_details(self, name):
        group = self.get_group(name)
        if group:
            return self._client.service.GetUserGroupDetails(self.token, group.outID)

    def create_group(self, name):
        if not self.get_group(name):
            base = self._client.service.GetUserGroupDetails(self.token, 'Create')
            group = copy.copy(base)
            group.ioName = name
            return self._client.service.ModifyUserGroupDetails(self.token, base, group)
        else:
            return None

    def delete_group(self, name):
        group = self.get_group(name)
        if group:
            group_wrapper = self._client.types.UsersWrapper(deep=True)
            group_wrapper.users.user = [group]
            self._client.service.DeleteUsers(self.token, group_wrapper)

    def get_workspaces(self):
        return self._client.service.GetWorkspaces(self.token, '').workspaces.workspace

    def get_workspace(self, name):
        workspaces = self.get_workspaces()
        for workspace in workspaces:
            if name in workspace.ioName:
                return workspace
        return None

    def get_workspace_details(self, name):
        workspace = self.get_workspace(name)
        if workspace:
            return self._client.service.GetWorkspaceDetails(self.token, workspace.outID)

    def create_workspace(self, name='default_name', capacity=100, *options):
        self.__check_name__(name)
        self.set_byte_count_divisor()
        base = self._client.service.GetWorkspaceDetails(self.token, 'Create')
        base.userAccesses = []
        base.outStorageGroups = []
        workspace = copy.copy(base)
        workspace.ioName = name
        workspace.ioByteCount = str(capacity)
        if self.server_info.serverType == ISIS_5000:
            workspace.ioProtectionMode = 16
        return self._client._service.ModifyWorkspaceDetails(self.token, base, workspace)

    def update_workspace_capacity(self, name="", capacity=None):
        workspace = self.get_workspace_details(name)
        #for k, v in kwargs.iteritems():
        #    if k == 'capacity':
        #        pass
        modify_workspace = copy.deepcopy(workspace)
        modify_workspace.ioByteCount = int(capacity)

        return self._client.service.ModifyWorkspaceDetails(self.token, workspace, modify_workspace)


    def delete_workspace(self, name):
        workspace = self.get_workspace(name)
        if workspace:
            workspace_wrapper = self._client.types.WorkspacesWrapper(deep=True)
            workspace_wrapper.workspaces.workspace = [workspace]
            self._client.service.DeleteWorkspaces(self.token, workspace_wrapper)


    def get_system_info(self):
        return self._client.service.GetSystemInfo(self.token)


    def used(self):
        infos = self.get_server_info()
        used = float(infos['sysdirInfo']['sgUsedByteCount']) / 1024 / 1024 / 1024 / 1024
        return used


    def total(self):
        infos = self.get_server_info()
        total = float(infos['sysdirInfo']['sgByteCount']) / 1024 / 1024 / 1024 / 1024
        return total


    def _send(self, values):
        url = 'http://%s/v2/ida' % self.hostname
        authinfo = 'avidagent=12345; AdminServerToken=%s; AgentLoginName=%s' % \
                (self.token, self.username)
        headers = {'User-Agent': '12345', 'Cookie': authinfo}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req).read()
        if response:
            try:
                return xmltodict.parse(response)
            except xmltodict.expat.ExpatError:
                return eval(response)
        return None

    def get_server_info(self):
        """ Get basic information about your system and your network.
            Those informations are accessible from Avid import ISIS Launch Pad.
        """
        return self._send({'r': 'GetSystemDirectorInfo'})

    def get_sys_info(self):
        """ Get more complete information about your system and your network. """
        return self._send({'r': 'getSysInfo'})

    def get_installer_links(self):
        return self._send({'r': 'GetInstallerLinks'})

    def get_installer(self, platform):
        element_list = self.get_installer_links()['list']['list']
        for elmt in element_list:
            if elmt['@display'] == 'ISISClient/':
                for install in elmt['element']:
                    url = "http://"+self.hostname+'/'+install['url']
                    name = url.split('/')[-1:][0]
                    if platform in name:
                        found = True
                        urllib.urlretrieve(url, name)

    def get_snapshots(self):
        result = self._send({ 'r': 'GetSnapshots'})
        if isinstance(result, str):
            return None
        if result['snapShots']:
            return result['snapShots']
        return None

    def create_snapshot(self, name):
        return self._send({ 'r': 'GenerateNewSnapshot', 'name': name})

    def delete_snapshot(self, name):
        return self._send({ 'r': 'DeleteSnapshotFile', 'name': name})

    def create_archive(self, name):
        return self._send({ 'r': 'GenerateNewArchive', 'name': name})

    def delete_archive(self, name):
        return self._send({ 'r': 'DeleteArchiveFile', 'name': name})

    def get_netstats(self):
        """  Get statistics for IPv4 and IPv6, TCP and UDP. """
        return self._send({'r': 'getNetStatus'})

    def do_traceroute(self, host):
        """ Allows you to verify the path between a system in the shared
            storage network and the System Director.

            :param host: hostname or ip address
        """
        return self._send({'r': 'doTraceroute', 'host': host})

    def do_ping(self, host):
        """ Allows you to test the connection between a system in the shared
            storage network and the System Director.

            :param host: hostname or ip address
        """
        return self._send({'r': 'doPing', 'host': host})

    def get_event_log(self, type="System", count=100):
        """ Retrieve system messages, info, warnings and errors at the
            application, system and security level.

            :param type: select log type. Can be 'System', 'Application' or 'Security'
            :param count: number of event to retrieve

            :return: list of events
            :rtype: list
        """
        return self._send({'r': 'getEventLog', 'type': type, 'count': count})

    def get_admin_log(self):
        """ Retrieve current actions reported by the ISIS Management Console,
            including informational messages (such as when upgrades occur),
            errors, and warnings.

            :return: list of actions
            :rtype: list
        """
        return self._send({'r': 'GetAdminToolLogFile', 'lfName': 'AdminToolLog.csv'})

    def reset_status_event(self):
        """ Reset events into Avid ISIS Launch Pad.
        """
        res = self._send({'r': 'ResetEventStatus'})
        try:
            return res['cmd_result']['status'] == 'success'
        except:
            return False


