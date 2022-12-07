#!/usr/bin/env python3

import unittest
import types
import os
import importlib.machinery
from unittest.mock import MagicMock, Mock


def get_resource_path(relative_path):
    return os.path.join(os.path.dirname(__file__), relative_path)


# load standalone script as module
loader = importlib.machinery.SourceFileLoader("deployer_keycloak", get_resource_path("../bin/deployer_keycloak"))
deployer_keycloak_oidc = types.ModuleType(loader.name)
loader.exec_module(deployer_keycloak_oidc)


class TestDeployerKeycloak(unittest.TestCase):

    # Test the format is compatible with Keycloak
    def test_oidc_format_keycloak_msg(self):
        new_service = {
            "client_id": "testOidcId",
            "service_name": "testName",
            "service_description": "testDescription",
            "protocol": "oidc",
            "contacts": [
                {"name": "name1", "email": "email1", "type": "technical"},
                {"name": "name2", "email": "email2", "type": "security"},
            ],
        }
        out_service = {
            "attributes": {
                "client_credentials.use_refresh_token": "false",
                "contacts": "email1",
                "oauth2.device.authorization.grant.enabled": "false",
                "oauth2.token.exchange.grant.enabled": False,
                "oidc.ciba.grant.enabled": "false",
                "refresh.token.max.reuse": "0",
                "revoke.refresh.token": "false",
                "use.jwks.string": "false",
                "use.jwks.url": "false",
                "use.refresh.tokens": "false",
            },
            "clientId": "testOidcId",
            "consentRequired": False,
            "defaultClientScopes": ["example"],
            "description": "testDescription",
            "implicitFlowEnabled": False,
            "name": "testName",
            "protocol": "openid-connect",
            "publicClient": False,
            "serviceAccountsEnabled": False,
            "standardFlowEnabled": False,
            "webOrigins": ["+"],
        }

        func_result = deployer_keycloak_oidc.format_keycloak_msg(new_service, ["example"])
        self.assertEqual(func_result, out_service)

    # Test calling Keycloak to create a new entry
    def test_oidc_deploy_to_keycloak_create(self):
        new_service = {
            "client_id": "testOidcId",
            "service_name": "testName",
            "service_description": "testDescription",
            "protocol": "oidc",
            "contacts": [
                {"name": "name1", "email": "email1", "type": "technical"},
                {"name": "name2", "email": "email2", "type": "security"},
            ],
            "scope": [
                "openid",
                "email",
                "profile",
            ],
            "deployment_type": "create",
        }
        out_service = {
            "response": {
                "attributes": {
                    "client_credentials.use_refresh_token": "false",
                    "contacts": "email1",
                    "oauth2.device.authorization.grant.enabled": "false",
                    "oauth2.token.exchange.grant.enabled": False,
                    "oidc.ciba.grant.enabled": "false",
                    "refresh.token.max.reuse": "0",
                    "revoke.refresh.token": "false",
                    "use.jwks.string": "false",
                    "use.jwks.url": "false",
                    "use.refresh.tokens": "false",
                },
                "consentRequired": False,
                "optionalClientScopes": ["profile", "email"],
                "implicitFlowEnabled": "false",
                "publicClient": "false",
                "serviceAccountsEnabled": "false",
                "standardFlowEnabled": "false",
                "clientId": "testOidcId",
                "defaultClientScopes": ["example"],
                "description": "testDescription",
                "id": "a1a2a3a4-b5b6-c7c8-d9d0-testOidcId",
                "protocol": "openid-connect",
                "implicitFlowEnabled": False,
                "name": "testName",
                "publicClient": False,
                "serviceAccountsEnabled": False,
                "standardFlowEnabled": False,
            },
            "status": 201,
        }
        realm_default_client_scopes = {
            "response": [{"id": "a1a2a3a4-b5b6-c7c8-d9d0-testScope3", "name": "example", "protocol": "openid-connect"}],
            "status": 201,
        }

        mock = MagicMock()
        mock.create_client = MagicMock(return_value=out_service)
        mock.get_client_by_id = MagicMock(return_value=out_service)
        mock.get_realm_default_client_scopes = MagicMock(return_value=realm_default_client_scopes)

        service_account_config = {
            "service_account": {"attribute_name": "voPersonID", "candidate": "id", "scope": "example.org"}
        }

        func_result = deployer_keycloak_oidc.deploy_to_keycloak(new_service, mock, service_account_config)
        self.assertEqual(func_result, (out_service, "a1a2a3a4-b5b6-c7c8-d9d0-testOidcId", "testOidcId"))

    # Test calling Keycloak to delete an entry
    def test_oidc_deploy_to_keycloak_delete(self):
        new_service = {
            "external_id": "a1a2a3a4-b5b6-c7c8-d9d0-testOidcId",
            "client_id": "testOidcId",
            "service_name": "testName",
            "service_description": "testDescription",
            "protocol": "oidc",
            "contacts": [
                {"name": "name1", "email": "email1", "type": "technical"},
                {"name": "name2", "email": "email2", "type": "security"},
            ],
            "deployment_type": "delete",
        }
        out_service = {
            "response": "OK",
            "status": 200,
        }
        realm_default_client_scopes = {
            "response": [{"id": "a1a2a3a4-b5b6-c7c8-d9d0-testScope5", "name": "example", "protocol": "openid-connect"}],
            "status": 200,
        }

        mock = MagicMock()
        mock.delete_client = MagicMock(return_value=out_service)

        func_result = deployer_keycloak_oidc.deploy_to_keycloak(new_service, mock, "config")
        self.assertEqual(func_result, (out_service, "a1a2a3a4-b5b6-c7c8-d9d0-testOidcId", "testOidcId"))

    # Test calling Keycloak to update an entry
    def test_oidc_deploy_to_keycloak_update(self):
        new_service = {
            "external_id": "a1a2a3a4-b5b6-c7c8-d9d0-testOidcId",
            "client_id": "testOidcId",
            "service_name": "testName",
            "service_description": "testDescription",
            "protocol": "oidc",
            "contacts": [
                {"name": "name1", "email": "email1", "type": "technical"},
                {"name": "name2", "email": "email2", "type": "security"},
            ],
            "deployment_type": "edit",
            "scope": ["email", "eduperson_entitlement"],
        }
        out_service = {
            "response": {
                "attributes": {
                    "client_credentials.use_refresh_token": "false",
                    "contacts": "email1",
                    "oauth2.device.authorization.grant.enabled": "false",
                    "oauth2.token.exchange.grant.enabled": False,
                    "oidc.ciba.grant.enabled": "false",
                    "use.jwks.string": "false",
                    "use.jwks.url": "false",
                    "use.refresh.tokens": "false",
                },
                "consentRequired": False,
                "implicitFlowEnabled": "false",
                "publicClient": "false",
                "serviceAccountsEnabled": "false",
                "standardFlowEnabled": "false",
                "clientId": "testOidcId",
                "description": "testDescription",
                "id": "a1a2a3a4-b5b6-c7c8-d9d0-testOidcId",
                "protocol": "openid-connect",
                "implicitFlowEnabled": False,
                "name": "testName",
                "defaultClientScopes": ["example"],
                "publicClient": False,
                "serviceAccountsEnabled": False,
                "standardFlowEnabled": False,
                "optionalClientScopes": ["email", "profile"],
            },
            "status": 200,
        }
        realm_default_client_scopes = {
            "response": [{"id": "a1a2a3a4-b5b6-c7c8-d9d0-testScope7", "name": "example", "protocol": "openid-connect"}],
            "status": 200,
        }
        client_authz_permissions = {
            "response": {"enabled": False},
            "status": 200,
        }

        mock = MagicMock()
        mock.update_client = MagicMock(return_value=out_service)
        mock.get_realm_default_client_scopes = MagicMock(return_value=realm_default_client_scopes)
        mock.get_client_authz_permissions = MagicMock(return_value=client_authz_permissions)

        func_result = deployer_keycloak_oidc.deploy_to_keycloak(new_service, mock, "config")
        self.assertEqual(func_result, (out_service, "a1a2a3a4-b5b6-c7c8-d9d0-testOidcId", "testOidcId"))

    # Test update data with error when calling Keycloak
    def test_oidc_process_data_fail(self):
        new_msg = [
            {
                "id": 12,
                "client_id": "testOidcId",
                "service_name": "testName",
                "service_description": "testDescription",
                "contacts": [{"name": "name1", "email": "email1"}],
                "deployment_type": "create",
            }
        ]

        keycloak_config = {
            "auth_server": "https://example.com/auth",
            "realm": "example",
        }

        func_result = deployer_keycloak_oidc.process_data(new_msg, "", keycloak_config)
        self.assertEqual(
            func_result,
            [
                {
                    "attributes": {},
                    "data": {
                        "id": 12,
                        "status_code": 0,
                        "state": "error",
                        "error_description": "An error occurred while calling Keycloak",
                    },
                }
            ],
        )

    # Test update data calling Keycloak successfully
    def test_oidc_process_data_success(self):
        new_msg = [
            {
                "id": 12,
                "client_id": "testOidcId",
                "service_name": "testName",
                "service_description": "testDescription",
                "contacts": [{"name": "name1", "email": "email1"}],
                "deployment_type": "create",
            }
        ]
        deployer_keycloak_oidc.deploy_to_keycloak = MagicMock(
            return_value=({"status": 200}, "a1a2a3a4-b5b6-c7c8-d9d0-testOidcId", "testOidcId")
        )

        keycloak_config = {
            "auth_server": "https://example.com/auth",
            "realm": "example",
        }

        func_result = deployer_keycloak_oidc.process_data(new_msg, "token", keycloak_config)
        self.assertEqual(
            func_result,
            [
                {
                    "attributes": {},
                    "data": {
                        "id": 12,
                        "external_id": "a1a2a3a4-b5b6-c7c8-d9d0-testOidcId",
                        "status_code": 200,
                        "state": "deployed",
                        "client_id": "testOidcId",
                    },
                }
            ],
        )
