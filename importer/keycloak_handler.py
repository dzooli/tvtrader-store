"""
Keycloak token handler implementation.

This module provides a TokenHandler implementation for Keycloak authentication.
"""
import sys
from pathlib import Path

from keycloak import KeycloakGetError
from keycloak.keycloak_admin import KeycloakAdmin
from keycloak.keycloak_openid import KeycloakOpenID
from loguru import logger

# Add the parent directory to the Python path so that 'importer' can be found as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

from importer.tokenmanager import TokenHandler


class KeycloakTokenHandler(TokenHandler):
    """Token handler for Keycloak authentication."""

    def get_token(self, **kwargs) -> dict[str, str] | str:
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
            dict[str, str] | str: Keycloak token dictionary containing access_token, refresh_token,
                                 expires_in, and other fields

        Raises:
            KeyError: If there is an error retrieving the token
        """
        server_url = kwargs.get('server_url')
        client_id = kwargs.get('client_id')
        username = kwargs.get('username')
        password = kwargs.get('password')

        # Initialize KeycloakOpenID client
        logger.info(f"Initializing KeycloakOpenID client with server URL: {server_url}")
        keycloak_openid = KeycloakOpenID(
            server_url=server_url,
            client_id=client_id,
            realm_name='master'
        )

        try:
            # Get token using password grant
            logger.info(f"Getting token for user: {username}")
            logger.debug(f"Using password grant to get token for user: {username}")
            logger.debug(f"Using password: {password}")
            token = keycloak_openid.token(
                username=username,
                password=password,
                grant_type="password"
            )
            logger.success("Successfully obtained Keycloak token")
            logger.debug(f"Keycloak token: {token}")
            return token
        except Exception as exc:
            logger.error(f"Failed to get Keycloak token: {str(exc)}")
            raise KeyError(f"Failed to get Keycloak token: {str(exc)}")

    def get_client_secret(self, **kwargs) -> str:
        """
        Retrieves a client secret from Keycloak using the provided access token.

        Args:
            **kwargs: Must include:
                - access_token (dict or str): Keycloak access token used for authentication
                  If dict, it should be the full token dictionary returned by KeycloakOpenID.token()
                  If str, it will be used directly
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

        # Handle token based on its type
        token_param = access_token

        keycloak_admin = KeycloakAdmin(
            server_url=server_url,
            realm_name=realm_name,
            token=token_param
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

    def get_user_attribute(self, **kwargs) -> str:
        """
        Retrieves a user attribute from Keycloak using the provided access token.

        Args:
            **kwargs: Must include:
                - access_token (dict or str): Keycloak access token used for authentication
                  If dict, it should be the full token dictionary returned by KeycloakOpenID.token()
                  If str, it will be wrapped in {'access': access_token}
                - server_url (str): Keycloak server URL
                - realm_name (str): Keycloak realm name
                - username (str): Username to retrieve attribute for
                - attribute_name (str): Name of the attribute to retrieve

        Returns:
            str: The attribute value retrieved from Keycloak

        Raises:
            AttributeError: If the specified user or attribute is not found in Keycloak
            KeyError: If there is an error retrieving users or attributes from Keycloak
            ValueError: If the KeycloakAdmin client initialization fails
        """
        # Extract required parameters
        access_token = kwargs.get('access_token')
        server_url = kwargs.get('server_url')
        realm_name = kwargs.get('realm_name')
        username = kwargs.get('username')
        attribute_name = kwargs.get('attribute_name')

        # Initialize admin client and get users
        keycloak_admin = self._init_admin_client(access_token, server_url, realm_name)
        users = self._get_all_users(keycloak_admin)

        # Find target user and get attributes
        user_id, user_attributes = self._find_user_and_attributes(keycloak_admin, users)

        # Get and validate target attribute
        if not user_attributes or attribute_name not in user_attributes:
            user_attributes = self._get_user_attributes(keycloak_admin, user_id)

        if not user_attributes or attribute_name not in user_attributes:
            logger.error(f"Attribute {attribute_name} not found for user {username}")
            raise AttributeError(f"Attribute {attribute_name} not found for user {username}")

        attribute_value = user_attributes[attribute_name][0]
        logger.success(f"Successfully obtained attribute {attribute_name} from Keycloak")
        return attribute_value

    def _init_admin_client(self, access_token, server_url, realm_name):
        """Initialize Keycloak admin client"""
        logger.info(f"Initializing KeycloakAdmin client for realm: {realm_name}")
        token_param = {'access': access_token} if isinstance(access_token, str) else access_token

        keycloak_admin = KeycloakAdmin(
            server_url=server_url,
            realm_name=realm_name,
            token=token_param
        ) or None

        if not keycloak_admin:
            logger.error(f"Failed to initialize KeycloakAdmin client for realm: {realm_name}")
            raise ValueError(f"Failed to initialize KeycloakAdmin client for realm: {realm_name}")

        return keycloak_admin

    def _get_all_users(self, keycloak_admin):
        """Get all users from Keycloak"""
        logger.info("Getting all Keycloak users")
        try:
            users = keycloak_admin.get_users()
            if not users:
                logger.error("No users found in Keycloak")
                raise KeyError("No users found in Keycloak")
            logger.success("Successfully obtained all users from Keycloak")
            return users
        except KeycloakGetError:
            logger.error("Failed to get all users from Keycloak")
            raise KeyError("Failed to get all users from Keycloak")

    def _find_user_and_attributes(self, users, username):
        """Find user by username and get their attributes"""
        logger.info(f"Looking for user with username: {username}")
        for user in users:
            try:
                if user["username"] == username:
                    return user["id"], user.get("attributes", {})
            except KeyError:
                logger.error(f"User {user} does not have username")
                continue

        logger.error(f"User {username} not found in Keycloak")
        raise AttributeError(f"User {username} not found")

    def _get_user_attributes(self, keycloak_admin, user_id):
        """Get user attributes by user ID"""
        logger.info(f"Getting attributes for user ID: {user_id}")
        try:
            user = keycloak_admin.get_user(user_id)
            attributes = user.get("attributes", {})
            logger.debug(f"User: {user}")
            logger.debug(f"Successfully obtained user details for user ID: {attributes}")
            return attributes
        except KeycloakGetError:
            logger.error(f"Failed to get user details for user ID: {user_id}")
            raise KeyError(f"Failed to get user details for user ID: {user_id}")
