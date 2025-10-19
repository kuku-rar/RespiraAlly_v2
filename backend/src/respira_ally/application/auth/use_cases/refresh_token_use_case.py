"""
Refresh Token Use Case
Handles token refresh and rotation
"""
from respira_ally.core.config import settings
from respira_ally.core.exceptions.application_exceptions import UnauthorizedError
from respira_ally.core.schemas.auth import RefreshTokenResponse
from respira_ally.core.security.jwt import create_access_token, create_refresh_token, verify_token
from respira_ally.infrastructure.cache.token_blacklist_service import (
    TokenBlacklistService,
)


class RefreshTokenUseCase:
    """
    Refresh Token Use Case

    Flow:
    1. Verify refresh token
    2. Check if token is blacklisted
    3. Generate new access token
    4. Optionally generate new refresh token (token rotation)
    5. Blacklist old refresh token if rotation is enabled
    """

    def __init__(self, token_blacklist_service: TokenBlacklistService):
        self.token_blacklist_service = token_blacklist_service

    async def execute(
        self, refresh_token: str, rotate_refresh_token: bool = False
    ) -> RefreshTokenResponse:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: JWT refresh token
            rotate_refresh_token: If True, also generate new refresh token

        Returns:
            RefreshTokenResponse with new access token (and optionally new refresh token)

        Raises:
            UnauthorizedError: If refresh token is invalid or blacklisted
        """
        # Verify refresh token
        payload = verify_token(refresh_token, expected_type="refresh")

        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id or not role:
            raise UnauthorizedError("Invalid refresh token: missing user information")

        # Check if refresh token is blacklisted
        is_blacklisted = await self.token_blacklist_service.is_blacklisted(
            refresh_token, user_id=user_id
        )

        if is_blacklisted:
            raise UnauthorizedError("Refresh token has been revoked")

        # Generate new access token
        token_payload = {"sub": user_id, "role": role}
        new_access_token = create_access_token(token_payload)

        # Optional: Rotate refresh token (recommended for security)
        new_refresh_token = None
        if rotate_refresh_token:
            new_refresh_token = create_refresh_token(token_payload)

            # Blacklist old refresh token
            await self.token_blacklist_service.add_to_blacklist(refresh_token)

        return RefreshTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
