# -*- coding: utf-8 -*-

import sys
import urllib
import urllib2
from urllib2 import HTTPError, URLError
import copy
import suds
from suds.client import Client
from utils import xml2obj


ISIS_AGENT = '12345'
ISIS_SOAP_URL = 'http://{hostname}:{port}/?wsdl'
ISIS_SOAP_PORT = 80
ISIS_USER_READ = 1
ISIS_USER_WRITE = 3
ISIS_USER_NONE = 0
ISIS_IDA_URL='http://{hostname}:{port}/v2/ida&rndval=1421067633746'
ISIS_AUTH_INFO='avidagent=12345; AdminServerToken={token}; AgentLoginName={username}'


class Connection(object):

    def __init__(self, hostname, username, password, port=80):
        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port
        self._token = None
        self.server_url = ISIS_IDA_URL.format(hostname=self._hostname,
                                              port=self._port)
        self._check_hostname()
        self._login()

    def __repr__(self):
        return '{}("{}", "{}", "{}")'.format(
            self.__class__.__name__,
            self._hostname,
            self._username,
            self._password)

    def _check_hostname(self):
        try:
            url = urllib2.urlopen(self.server_url)
        except (HTTPError, URLError, Exception), e:
            print "Unable to connect: ",e

    def _login(self):
        values = {'r': 'createsession', 'user': self._username,
                  'pass': self._password}
        result = self._send(values)
        self._token = result.value

    def _send(self, values):
        authinfo = ISIS_AUTH_INFO.format(token=self._token,
                                         username=self._username)
        headers = {'User-Agent': '12345', 'Cookie': authinfo}
        data  = urllib.urlencode(values)
        req = urllib2.Request(self.server_url, data, headers)
        response = urllib2.urlopen(req).read()
        obj = xml2obj(response)
        if not isinstance(obj, basestring):
            if obj.code == '151':
                raise Exception('Authentication error: %s' % obj.msg)
        return obj


class SOAPConnection(Connection):

    def __init__(self, hostname, username, password):
        Connection.__init__(self, hostname, username, password)
 
        url = ISIS_SOAP_URL.format(hostname=self._hostname,
                                   port=ISIS_SOAP_PORT)
        self._client = Client(url)
        self._client.options.cache.setduration(days=31)
        self.set_byte_count_divisor('1048576')

    def __del__(self):
        if self._token:
            self._client.service.Logout(self._token)

    def get_byte_count_divisor(self):
        return self._client.service.GetByteCountDivisor(self._token)

    def set_byte_count_divisor(self, byteCnt):
        return self._client.service.SetByteCountDivisor(self._token, byteCnt)

    def get_users(self):
        return self._client.service.GetUsers(self._token)['users']['user']

    def get_user(self, name):
        users = self.get_users()
        for user in users:
            if name in user.ioName:
                return user
        return None

    def get_user_details(self, name):
        user = self.get_user(name)
        if user:
            return self._client.service.GetUserDetails(self._token, user.outID)
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
        self.__check_name__(name)
        base = self._client.service.GetUserDetails(self._token, 'Create')
        user = copy.copy(base)
        user.ioName = name
        return self._client.service.ModifyUserDetails(self._token, base, user)

    def delete_user(self, name):
        user = self.get_user(name)
        if user:
            user_wrapper = self.client.factory.create('ns1:UsersWrapper')
            user_wrapper.users.user = [user]
            return self._client.service.DeleteUsers(self._token, user_wrapper)

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
                wp_access = self._client.factory.create('ns1:WorkspaceAccess')
                wp_access.outID = workspace_to_add.outID
                wp_access.outName = workspace_to_add.ioName
                wp_access.ioAccess = permissions
                modify_user.workspaceAccesses.access = [wp_access]
                return self._client.service.ModifyUserDetails(self._token,
                                                          user, modify_user)
            else:
                return None
        else:
            return None

    def get_groups(self):
        return self._client.service.GetUserGroups(self._token)['usergroups']['user']

    def get_group(self, name):
        groups = self.get_groups()
        for group in groups:
            if name in group.ioName:
                return group
        return None

    def get_group_details(self, name):
        group = self.get_group(name)
        if group:
            return self._client.service.GetUserGroupDetails(self._token, group.outID)

    def create_group(self, name):
        self.__check_name__(name)
        base = self._client.service.GetUserGroupDetails(self._token, 'Create')
        group = copy.copy(base)
        group.ioName = name
        return self._client.service.ModifyGroupDetails(self._token, base, group)

    def delete_group(self, name):
        group = self.get_group(name)
        if group:
            group_wrapper = self.client.factory.create('ns1:UsersWrapper')
            group_wrapper.users.user = [group]
            self._client.service.DeleteUsers(self._token, group_wrapper)

    def get_workspaces(self):
        return self._client.service.GetWorkspaces(self._token)['workspaces']['workspace']

    def get_workspace(self, name):
        workspaces = self.get_workspaces()
        for workspace in workspaces:
            if name in workspace.ioName:
                return workspace
        return None

    def get_workspace_details(self, name):
        workspace = self.get_workspace(name)
        if workspace:
            return self._client.service.GetWorkspaceDetails(self._token, workspace.outID)

    def create_workspace(self, name='default_name', capacity=100, *options):
        self.__check_name__(name)
        self.set_byte_count_divisor()
        base = self._client.service.GetWorkspaceDetails(self._token, 'Create')
        base.userAccesses = []
        base.outStorageGroups = []
        workspace = copy.copy(base)
        workspace.ioName = name
        workspace.ioByteCount = str(capacity)

        if self.server_info.serverType == ISIS_5000:
            workspace.ioProtectionMode = 16

        return self.client._service.ModifyWorkspaceDetails(self._token, base, workspace)

    def delete_workspace(self, name):
        workspace = self.get_workspace(name)
        if workspace:
            workspace_wrapper = self._client.factory.create('ns1:WorkspacesWrapper')
            workspace_wrapper.workspaces.workspace = [workspace]
            self._client.service.DeleteWorkspaces(self._token, workspace_wrapper)


class WEBConnection(Connection):

    def __init__(self, hostname, username, password):
        Connection.__init__(self, hostname, username, password)

    def get_server_info(self):
        return self._send({'r': 'GetSystemDirectorInfo'})

    def get_installer_links(self):
        values = {'r': 'GetInstallerLinks'}
        return self._send(values)

    def get_installer(self, platform):
        element_list = self.get_installer_links()['list']
        for elmt in element_list:
            if elmt['display'] == 'ISISClient/':
                for install in elmt['element']:
                    url = "http://"+conn._hostname+'/'+install.url
                    name = url.split('/')[-1:][0]
                    if platform in name:
                        found = True
                        urllib.urlretrieve(url, name)

    def get_snapshots(self):
        result = self._send({ 'r': 'GetSnapshots'})

        if isinstance(result, str):
            return None
        if result.snapshot:
            return result.snapshot
        return None

    def create_snapshot(self, name):
        result = self._send({ 'r': 'GenerateNewSnapshot', 'name': name})
        return result

    def delete_snapshot(self, name):
        return self._send({ 'r': 'DeleteSnapshotFile', 'name': name})

    def create_archive(self, name):
        return self._send({ 'r': 'GenerateNewArchive', 'name': name})

    def delete_archive(self, name):
        return self._send({ 'r': 'DeleteArchiveFile', 'name': name})

    def get_netstats(self):
        result = self._send({'r': 'getNetStatus'})
        return result.results

    def do_traceroute(self):
        return self._send({'r': 'doTraceroute', 'host': host})

    def do_ping(self, host):
        return self._send({'r': 'doPing', 'host': host})


