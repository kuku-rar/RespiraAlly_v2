"""
Logout Use Case
Handles token revocation and user logout
"""
from datetime import datetime, timezone

from respira_ally.core.exceptions.application_exceptions import UnauthorizedError
from respira_ally.core.security.jwt import verify_token
from respira_ally.infrastructure.cache.token_blacklist_service import (
    TokenBlacklistService,
)


class LogoutUseCase:
    """
    Logout Use Case

    Flow:
    1. Verify access token
    2. Add token to blacklist
    3. Optionally revoke all user tokens (logout from all devices)
    """

    def __init__(self, token_blacklist_service: TokenBlacklistService):
        self.token_blacklist_service = token_blacklist_service

    async def execute(self, access_token: str, revoke_all_tokens: bool = False) -> bool:
        """
        Logout user by revoking token(s)

        Args:
            access_token: JWT access token to revoke
            revoke_all_tokens: If True, revoke all tokens for this user

        Returns:
            True if logout successful

        Raises:
            UnauthorizedError: If token is invalid
        """
        # Verify token (will raise UnauthorizedError if invalid)
        payload = verify_token(access_token, expected_type="access")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid token: missing user ID")

        # Add current token to blacklist
        success = await self.token_blacklist_service.add_to_blacklist(access_token)

        if not success:
            raise UnauthorizedError("Failed to revoke token")

        # Optionally revoke all tokens for this user
        if revoke_all_tokens:
            await self.token_blacklist_service.revoke_all_user_tokens(
                user_id=user_id, issued_before=datetime.now(timezone.utc)
            )

        return True
