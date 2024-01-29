from __future__ import annotations
import typing as t
import itertools
import json
import string
import unicodedata
import hashlib
import numbers
import re
from . import Utils
from .exceptions import SynapsisError
from ..synapse import Synapse, SynapsePermission
from ..synapse.synapse_permission import PermissionCode, AccessTypes
import synapseclient
from synapseclient.core.utils import id_of
from synapseclient.core.exceptions import SynapseFileNotFoundError, SynapseHTTPError, SynapseAuthenticationError


class SynapsisUtils(object):
    def __init__(self, synapse: Synapse):
        self.__synapse__ = synapse

    def id_of(self,
              obj: synapseclient.Entity | str | dict | numbers.Number
              ) -> str | numbers.Number:
        """
        Try to figure out the Synapse ID of the given object.

        :param obj: String, Entity object, or dictionary.
        :return: The ID or throws an exception.
        """
        return id_of(obj)

    def is_synapse_id(self,
                      value: str,
                      exists: bool = False
                      ) -> bool:
        """
        Gets if the value is a Synapse ID and optionally if the Entity exists.

        :param value: String to check.
        :param exists: Check if the Entity exists otherwise only validates the value is a Synapse ID.
        :return: True if the value matches the Synapse ID format otherwise False.
        """
        if isinstance(value, str):
            value = value.strip()
            is_id = re.match('^syn[0-9]+$', value, re.IGNORECASE) is not None
            if is_id and exists:
                try:
                    bundle = self.get_bundle(value)
                    return bundle is not None
                except SynapseFileNotFoundError:
                    return False
                except (SynapseHTTPError, SynapseAuthenticationError,) as err:
                    status = (err.__context__ and err.__context__.response.status_code) or err.response.status_code
                    if status in (400, 404):
                        return False
                    # Valid ID but user lacks permission or is not logged in
                    elif status == 403:
                        return True
                return False
            else:
                return is_id
        return False

    def find_entity(self,
                    name: str,
                    parent: t.Optional[synapseclient.Entity | str] = None,
                    **get_kwargs: t.Optional[dict]
                    ) -> str | None:
        """
        Find an Entity given its name and parent.

        :param name: Name of the entity to find
        :param parent: An Entity object or the ID of an entity as a string. Omit if searching for a Project by name.
        :param get_kwargs: Keyword args for Synapse.get().
        :return: The Entity or None.
        """
        id = self.__synapse__.findEntityId(name, parent=parent)
        if id:
            return self.__synapse__.get(id, **get_kwargs)
        else:
            return None

    def delete_skip_trash(self,
                          entity: synapseclient.Entity | str
                          ) -> None:
        """
        Delete an entity and skip the trash. This permanently deletes the Entity.

        :param entity:
        :return: None
        """
        self.__synapse__.restDELETE(uri='/entity/{0}?skipTrashCan=true'.format(self.id_of(entity)))

    def get_bundle(self,
                   entity: synapseclient.Entity | str,
                   version: t.Optional[int] = None,
                   include_entity: t.Optional[bool] = True,
                   include_annotations: t.Optional[bool] = False,
                   include_permissions: t.Optional[bool] = False,
                   include_entity_path: t.Optional[bool] = False,
                   include_has_children: t.Optional[bool] = False,
                   include_access_control_list: t.Optional[bool] = False,
                   include_file_handles: t.Optional[bool] = False,
                   include_table_bundle: t.Optional[bool] = False,
                   include_root_wiki_id: t.Optional[bool] = False,
                   include_benefactor_acl: t.Optional[bool] = False,
                   include_doi_association: t.Optional[bool] = False,
                   include_file_name: t.Optional[bool] = False,
                   include_thread_count: t.Optional[bool] = False,
                   include_restriction_information: t.Optional[bool] = False
                   ) -> dict:
        """
        Gets the bundle for an Entity.

        :return: dict
        """
        request = {
            'includeEntity': include_entity,
            'includeAnnotations': include_annotations,
            'includePermissions': include_permissions,
            'includeEntityPath': include_entity_path,
            'includeHasChildren': include_has_children,
            'includeAccessControlList': include_access_control_list,
            'includeFileHandles': include_file_handles,
            'includeTableBundle': include_table_bundle,
            'includeRootWikiId': include_root_wiki_id,
            'includeBenefactorACL': include_benefactor_acl,
            'includeDOIAssociation': include_doi_association,
            'includeFileName': include_file_name,
            'includeThreadCount': include_thread_count,
            'includeRestrictionInformation': include_restriction_information
        }
        if version is not None:
            return self.__synapse__.restPOST('/entity/{0}/version/{1}/bundle2'.format(self.id_of(entity), version),
                                             body=json.dumps(request))
        else:
            return self.__synapse__.restPOST('/entity/{0}/bundle2'.format(self.id_of(entity)),
                                             body=json.dumps(request))

    def copy_file_handles_batch(self,
                                file_handle_ids: list[str],
                                obj_types: list[str],
                                obj_ids: list[str]
                                ) -> list[dict]:
        """
        Copies multiple filehandles.

        :param file_handle_ids: The filehandle IDs to copy.
        :param obj_types: The types of the associated object.
        :param obj_ids: The IDS of the associated objects.
        :return: List of dict
        """
        copy_file_handle_request = {"copyRequests": []}
        for file_handle_id, obj_type, obj_id in itertools.zip_longest(file_handle_ids, obj_types, obj_ids):
            file_item = {
                "originalFile": {
                    "fileHandleId": file_handle_id,
                    "associateObjectId": obj_id,
                    "associateObjectType": obj_type
                }
            }
            copy_file_handle_request["copyRequests"].append(file_item)

        copy_response = self.__synapse__.restPOST('/filehandles/copy',
                                                  body=json.dumps(copy_file_handle_request),
                                                  endpoint=self.__synapse__.fileHandleEndpoint)
        copy_results = copy_response.get("copyResults")
        for copy_result in copy_results:
            if copy_result.get("failureCode", None) is not None:
                error = 'Error copying filehandle: {0}, dataFileHandleId: {1}'.format(
                    copy_result["failureCode"],
                    copy_result['originalFileHandleId']
                )
                raise SynapsisError(error)

        return copy_results

    def get_project(self,
                    entity: synapseclient.Entity | str,
                    id_only: bool = False
                    ) -> synapseclient.Project | str:
        """
        Gets the Project or ID for a child entity.

        :param entity: The Entity to get the Project for.
        :param id_only: True to only return the Project's ID.
        :return: Project or ID
        """
        if isinstance(entity, synapseclient.Project):
            if id_only:
                return self.id_of(entity)
            else:
                return entity

        path = self.__synapse__.restGET('/entity/{0}/path'.format(self.id_of(entity))).get('path')[1:][0]
        if id_only:
            return path['id']
        else:
            return self.__synapse__.get(path['id'])

    def get_synapse_path(self,
                         entity: synapseclient.Entity | str
                         ) -> str:
        """
        Gets the absolute path to a Synapse Entity.

        :param entity: Synapse Entity or ID to get the path for.
        :return: str
        """
        paths = self.__synapse__.restGET('/entity/{0}/path'.format(self.id_of(entity))).get('path')[1:]
        segments = Utils.map(paths, key='name')
        return '/'.join(segments)

    def find_data_file_handle(self,
                              source: list[dict] | synapseclient.File | dict,
                              data_file_handle_id: t.Optional[str] = None
                              ) -> dict:
        """
        Gets the fileHandle from an entity, bundle, or list of filehandles.

        :param source: List of bundle["fileHandles"], File, or File bundle to get the filehandle from.
        :param data_file_handle_id: The dataFileHandleId to find.
        :return: dict or None
        """
        file_handles = None
        if isinstance(source, synapseclient.File):
            return source['_file_handle']
        elif isinstance(source, dict):
            data_file_handle_id = source.get('entity', {}).get('dataFileHandleId', None)
            file_handles = source.get('fileHandles', [])
        elif isinstance(source, list):
            file_handles = source

        if data_file_handle_id is None:
            return Utils.find(file_handles, lambda f: f['status'] == 'AVAILABLE' and not f['isPreview'])
        else:
            return Utils.find(file_handles, lambda f: str(f['id']) == str(data_file_handle_id))

    def find_acl_resource_access(self,
                                 acl: dict,
                                 principal: synapseclient.UserProfile | synapseclient.Team | str | numbers.Number
                                 ) -> dict | None:
        """
        Finds the resourceAccess from an ACL for a User or Team.

        :param acl: The ACL to get the access from.
        :param principal: The UserProfile, Team, or ID to get access for.
        :return: dict or None
        """
        principal_id = self.id_of(principal)
        resource_access = Utils.find((acl or {}).get('resourceAccess', []) or [],
                                     lambda a: str(a.get('principalId')) == str(principal_id),
                                     default=None)
        return resource_access

    def get_filehandle(self,
                       file: synapseclient.File | str
                       ) -> dict | None:
        """
        Gets the filehandle for an Entity.

        :param file: File Entity or ID
        :return: dict
        """
        response = self.__synapse__.restGET('/entity/{0}/filehandles'.format(self.id_of(file)))
        filehandle = self.find_data_file_handle(response['list'])
        return filehandle

    def get_filehandles(self,
                        files_and_file_handles: list[tuple],
                        include_pre_signed_urls: t.Optional[bool] = False,
                        include_preview_pre_signed_urls: t.Optional[bool] = False
                        ) -> list[dict]:
        """
        Gets multiple filehandles at once.

        :param files_and_file_handles: List of tuples with (Entity File or ID, file_handle_id or dict with 'id')
        :param include_pre_signed_urls: True to include pre-signed URLs.
        :param include_preview_pre_signed_urls: True to include pre-signed URLs for preview.
        :return: List of dict
        """
        body = {
            'includeFileHandles': True,
            'includePreSignedURLs': include_pre_signed_urls,
            'includePreviewPreSignedURLs': include_preview_pre_signed_urls,
            'requestedFiles': []
        }
        for syn_file, file_handle in files_and_file_handles:
            body['requestedFiles'].append(
                {
                    'fileHandleId': self.id_of(file_handle),
                    'associateObjectId': self.id_of(syn_file),
                    'associateObjectType': 'FileEntity'
                }
            )

        response = self.__synapse__.restPOST('/fileHandle/batch',
                                             endpoint=self.__synapse__.fileHandleEndpoint,
                                             body=json.dumps(body))

        return response.get('requestedFiles', [])

    def get_entity_permission(self,
                              entity: synapseclient.Entity | str,
                              principal: synapseclient.UserProfile | synapseclient.Team | str | numbers.Number
                              ) -> SynapsePermission:
        """
        Gets the permission on an Entity for a user or team.

        :param entity: The Entity or ID to get the permission from.
        :param principal: The UserProfile, Team, or ID to get permission for.
        :return: SynapsePermission
        """
        principal_id = self.id_of(principal)
        current_access_types = self.__synapse__.getPermissions(entity, principalId=principal_id)
        return SynapsePermission.get(current_access_types, SynapsePermission.NO_PERMISSION)

    def set_entity_permission(self,
                              entity: synapseclient.Entity | str,
                              principal: synapseclient.UserProfile | synapseclient.Team | str | numbers.Number,
                              permission: SynapsePermission | PermissionCode | AccessTypes | None,
                              **set_permissions_kwargs: t.Optional[dict]
                              ) -> dict:
        """
        Set the permission on an Entity for a user or team.

        :param entity: The Entity or ID to set the permission on.
        :param principal: The UserProfile, Team, or ID to change the permission for.
        :param permission: SynapsePermission, SynapsePermission.code, list of permissions, or None to remove the permission.
        :param set_permissions_kwargs: Keyword args for Synapse.setPermissions().
        :return: dict
        """
        permission = SynapsePermission.get(permission, SynapsePermission.NO_PERMISSION)
        principal_id = self.id_of(principal)
        return self.__synapse__.setPermissions(entity,
                                               principal_id,
                                               accessType=permission.access_types,
                                               **set_permissions_kwargs)

    def invite_to_team(self,
                       team: synapseclient.Team | str | numbers.Number,
                       invitee: synapseclient.UserProfile | str | numbers.Number,
                       message: t.Optional[str] = None,
                       force: t.Optional[bool] = False,
                       as_manager: t.Optional[bool] = False
                       ) -> dict | list[dict, dict] | None:
        """
        Invite a user or email address to a Team.

        :param team: The Team or ID to invite to.
        :param invitee: The UserProfile, UserProfile.Id, or email address to invite.
        :param message: Optional message to include in the invitation email sent to the invitee.
        :param force: Force a new invitation to be sent if one already exists.
        :param as_manager: True to invite the user as a Manager of the Team. Only applicable for Users, not emails.
        :return: dict of invite response and/or invite response/team manager response.
        """
        is_email = True if (isinstance(invitee, str) and '@' in invitee) else False
        if is_email and as_manager:
            raise SynapsisError('Cannot invite emails as managers.')

        invite_args = {
            'message': message,
            'force': force
        }

        if is_email:
            invite_args['inviteeEmail'] = invitee
        else:
            invite_args['user'] = invitee

        invite = self.__synapse__.invite_to_team(team, **invite_args)

        if as_manager:
            manager_res = self.set_team_permission(team, invitee, SynapsePermission.TEAM_MANAGER)
            return [invite, manager_res]
        else:
            return invite

    def remove_from_team(self,
                         team: synapseclient.Team | str | numbers.Number,
                         user: synapseclient.UserProfile | str | numbers.Number
                         ) -> None:
        """
        Removes a user from a Team.

        :param team: The Team or ID to remove the user from.
        :param user: The UserProfile or ID to remove from the Team.
        :return: None
        """
        team_id = self.id_of(team)
        user_id = self.id_of(user)
        self.__synapse__.restDELETE(uri='/team/{0}/member/{1}'.format(team_id, user_id))

    def get_team_members(self,
                         team: synapseclient.Team | str | numbers.Number,
                         users: list[synapseclient.UserProfile | str | numbers.Number] |
                                synapseclient.UserProfile | str | numbers.Number = None,
                         as_user_group_header: bool = False,
                         team_members: list[dict] | None = None,
                         ):
        """
        Gets the list of members on a team.

        :param team: Team or ID to get members from.
        :param users: Optional. Only return results for these users.
        :param as_user_group_header: True to return the "member" (UserGroupHeader) instead of the TeamMember.
        :param team_members: Optional. List of dictionaries from syn.getTeamMembers().
        :return: List of TeamMember objects or UserGroupHeader objects.
        """
        team_id = str(self.id_of(team))
        team_members = team_members or list(self.__synapse__.getTeamMembers(team))
        if users:
            users = users if isinstance(users, list) else [users]
            user_ids = Utils.map(users, lambda user: str(self.id_of(user)))
            team_members = Utils.select(
                team_members,
                lambda member: str(member.get('teamId')) == team_id and member.get('member').get('ownerId') in user_ids
            )

        if as_user_group_header:
            return Utils.map(team_members, key='member')
        else:
            return team_members

    def get_team_member(self,
                        team: synapseclient.Team | str | numbers.Number,
                        user: synapseclient.UserProfile | str | numbers.Number,
                        as_user_group_header: bool = False,
                        team_members: list[dict] | None = None,
                        ) -> dict | None:
        """
        Gets a member of a team.

        :param team: Team or ID to get members from.
        :param user: The UserProfile or ID to get.
        :param as_user_group_header: True to return the "member" (UserGroupHeader) instead of the TeamMember.
        :param team_members: Optional. List of dictionaries from syn.getTeamMembers().
        :return: List of TeamMember objects or UserGroupHeader objects.
        """
        return Utils.first(self.get_team_members(team,
                                                 users=user,
                                                 team_members=team_members,
                                                 as_user_group_header=as_user_group_header))

    def get_team_permission(self,
                            team: synapseclient.Team | str | numbers.Number,
                            user: synapseclient.UserProfile | str | numbers.Number,
                            **kwargs: t.Optional[dict]
                            ) -> SynapsePermission:
        """
        Gets the permission on a Team for a user.

        :param team: The Team or ID to get the permission from.
        :param user: The UserProfile or ID to get permission for.
        :return: SynapsePermission
        """
        team_id = self.id_of(team)
        team_acl = self.__synapse__.restGET('/team/{0}/acl'.format(team_id))
        user_access = self.find_acl_resource_access(team_acl, user)
        current_access_types = user_access['accessType'] if user_access else None
        current_permission = SynapsePermission.get(current_access_types, SynapsePermission.NO_PERMISSION)

        if kwargs.get('with_acl', False) is True:
            return current_permission, team_acl, user_access
        else:
            return current_permission

    def set_team_permission(self,
                            team: synapseclient.Team | str | numbers.Number,
                            user: synapseclient.UserProfile | str | numbers.Number,
                            permission: SynapsePermission | PermissionCode | AccessTypes | None
                            ) -> dict | None:
        """
        Set the permission for a User on a Team.

        :param team: The Team or ID to set the permission on.
        :param user: The UserProfile or ID to give permission to.
        :param permission: The permission to add or remove.
        :return: dict or None
        """
        permission = SynapsePermission.get(permission, SynapsePermission.NO_PERMISSION)
        current_permission, team_acl, user_access = self.get_team_permission(team, user, with_acl=True)

        if permission.equals(current_permission):
            return None
        else:
            if permission.none:
                if user_access is not None:
                    # Remove the permission.
                    team_acl['resourceAccess'].remove(user_access)
                else:
                    # Permission is being set to none and user has no access so nothing to update.
                    return None
            elif user_access:
                # Update the existing permission for the user.
                user_access['accessType'] = permission.access_types
            else:
                # Add a new permission for the user.
                new_acl = {'principalId': self.id_of(user), 'accessType': permission.access_types}
                team_acl['resourceAccess'].append(new_acl)
            return self.__synapse__.restPUT("/team/acl", body=json.dumps(team_acl))

    def md5sum(self,
               filename: str,
               chunk_blocks: t.Optional[int] = 12800,
               as_bytes: t.Optional[bool] = False
               ) -> str | bytes:
        """
        Gets the MD5 value for a file.

        :param filename: Path to the file.
        :param chunk_blocks: Read chunk block size. Will be multiplied by md5.block_size.
        :param as_bytes: True to return the MD5 as bytes, otherwise string.
        :return: str or bytes.
        """
        md5 = hashlib.md5()
        with open(filename, 'rb') as f:
            while chunk := f.read(chunk_blocks * md5.block_size):
                md5.update(chunk)
        if as_bytes:
            return md5.digest()
        else:
            return md5.hexdigest()

    __ENTITY_NAME_MAX_LEN__: t.Final[int] = 256
    __ENTITY_NAME_ALLOWED_CHARS__: t.Final[frozenset] = frozenset(
        list("'()+,-._ %s%s" % (string.ascii_letters, string.digits))
    )

    def sanitize_entity_name(self,
                             name: str,
                             replace_char: t.Optional[str] = '_',
                             return_replaced: t.Optional[bool] = False
                             ) -> str | list[str, list]:
        """
        Sanitizes the name for an Entity or File.

            The name of an entity.
                - Must be 256 characters or less.
                - May only contain: letters, numbers, spaces, underscores, hyphens, periods, plus signs, apostrophes, and parentheses
                - Not documented but can also accept commas.
        :param name: The name to sanitize.
        :param replace_char: The character you use as a replacement.
        :param return_replaced: True to return a list of the replaced characters with the sanitized name.
        :return: The sanitized string or the sanitized string and a list of replaced characters.
        """
        cleaned = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore')
        new_name = []
        replaced = []
        for char in [chr(c) for c in cleaned]:
            if char in self.__ENTITY_NAME_ALLOWED_CHARS__:
                new_name.append(char)
            else:
                new_name.append(replace_char)
                if char not in replaced:
                    replaced.append(char)
        new_name = ''.join(new_name)

        if len(new_name) > self.__ENTITY_NAME_MAX_LEN__:
            raise SynapsisError(
                'Entity name exceeds limit of: {0}, Name: {1}'.format(self.__ENTITY_NAME_MAX_LEN__, new_name))

        if return_replaced:
            return new_name, replaced
        else:
            return new_name
