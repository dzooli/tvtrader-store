"""
Keycloak token handler implementation.

This module provides a TokenHandler implementation for Keycloak authentication.
"""
from keycloak import KeycloakGetError
from keycloak.keycloak_admin import KeycloakAdmin
from keycloak.keycloak_openid import KeycloakOpenID
from loguru import logger

from importer.token_manager.base import TokenHandler


class KeycloakTokenHandler(TokenHandler):
    """Token handler for Keycloak authentication."""

    def get_token(self, **kwargs) -> str:
        """
        Get a token from Keycloak.

        Args:
            **kwargs: Must include:
                - server_url (str): Keycloak server URL
                - client_id (str): Keycloak client ID
                - username (str): Keycloak username
                - password (str): Keycloak password
                - realm_name (str, optional): Keycloak realm name, defaults to "master"

        Returns:
            str: Keycloak access token

        Raises:
            KeyError: If there is an error, retrieve the token
        """
        server_url = kwargs.get('server_url')
        client_id = kwargs.get('client_id')
        username = kwargs.get('username')
        password = kwargs.get('password')
        realm_name = kwargs.get('realm_name', 'master')

        # Initialize KeycloakOpenID client
        logger.info(f"Initializing KeycloakOpenID client with server URL: {server_url}")
        keycloak_openid = KeycloakOpenID(
            server_url=server_url,
            client_id=client_id,
            realm_name=realm_name
        )

        try:
            # Get token using password grant
            logger.info(f"Getting token for user: {username}")
            token = keycloak_openid.token(
                username=username,
                password=password,
                grant_type="password"
            )
            logger.success("Successfully obtained Keycloak token")
            return token["access_token"]
        except Exception as exc:
            logger.error(f"Failed to get Keycloak token: {str(exc)}")
            raise KeyError(f"Failed to get Keycloak token: {str(exc)}")

    def get_client_secret(self, **kwargs) -> str:
        """
        Retrieves a client secret from Keycloak using the provided access token.

        Args:
            **kwargs: Must include:
                - access_token (str): Keycloak access token used for authentication
                - server_url (str): Keycloak server URL
                - realm_name (str): Keycloak realm name
                - client_secret_id (str): Client ID to retrieve secret for

        Returns:
            str: The client secret string retrieved from Keycloak

        Raises:
            AttributeError: If the specified client is not found in Keycloak
            KeyError: If there is an error retrieving clients or client secret from Keycloak
            ValueError: If the KeycloakAdmin client initialization fails
        """
        access_token = kwargs.get('access_token')
        server_url = kwargs.get('server_url')
        realm_name = kwargs.get('realm_name')
        client_secret_id = kwargs.get('client_secret_id')

        # Initialize KeycloakAdmin client
        logger.info(f"Initializing KeycloakAdmin client for realm: {realm_name}")
        keycloak_admin = KeycloakAdmin(
            server_url=server_url,
            realm_name=realm_name,
            token={'access': access_token}
        ) or None
        if not keycloak_admin:
            logger.error(f"Failed to initialize KeycloakAdmin client for realm: {realm_name}")
            raise ValueError(f"Failed to initialize KeycloakAdmin client for realm: {realm_name}")

        # Get all clients
        logger.info("Getting all Keycloak clients")

        try:
            clients = keycloak_admin.get_clients()
        except KeycloakGetError:
            logger.error("Failed to get all clients from Keycloak")
            raise KeyError("Failed to get all clients from Keycloak")

        if not clients:
            logger.error("No clients found in Keycloak")
            raise KeyError("No clients found in Keycloak")

        logger.success("Successfully obtained all clients from Keycloak")

        # Find the client by clientId
        logger.info(f"Looking for client with ID: {client_secret_id}")
        client_id = None
        for cl in clients:
            try:
                if cl["clientId"] == client_secret_id:
                    client_id = cl["id"]
                    logger.info(f"Found client with ID: {client_id}")
                    break
            except KeyError:
                logger.error(f"Client {cl} does not have clientId")
                raise KeyError(f"Client {cl} does not have clientId")

        if not client_id:
            logger.error(f"Client {client_secret_id} not found in Keycloak")
            raise AttributeError(f"Client {client_secret_id} not found")

        # Get client secret
        logger.info(f"Getting client secret for client ID: {client_id}")
        try:
            client_secret = keycloak_admin.get_client_secrets(client_id)[0]
        except KeycloakGetError:
            logger.error(f"Failed to get client secret for client ID: {client_id}")
            raise KeyError(f"Failed to get client secret for client ID: {client_id}")

        logger.success("Successfully obtained client secret from Keycloak")

        return client_secret
