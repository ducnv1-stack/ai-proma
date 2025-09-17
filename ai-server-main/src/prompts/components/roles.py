
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class RoleType(Enum):
    """Enumeration of available AI assistant roles."""
    FACEBOOK_MARKETING = "marketing"

@dataclass(frozen=True)
class Role:
    """Immutable role configuration."""
    name: str
    description: str
    
    def __post_init__(self):
        """Validate role configuration after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Role name cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("Role description cannot be empty")

class RoleManager:
    """Manages AI assistant role definitions and retrieval."""
    
    _ROLE_DEFINITIONS = {
        RoleType.FACEBOOK_MARKETING: Role(
            name="SUPERB - Facebook Marketing",
            description=(
                "You are Famarex – an outstanding Facebook Marketing Specialist created by Superb AI"
                "You are responsible for building Facebook marketing plans, creating post content, generating images, publishing posts to Facebook Pages, and analyzing marketing results on Facebook Pages."
                "You will need to gather minimal information to help the user"
            )
        ),
    }
    
    @classmethod
    def get_role(cls, role_type: RoleType = RoleType.FACEBOOK_MARKETING) -> Role:
        """
        Retrieve a role configuration by type.
        
        Args:
            role_type: The type of role to retrieve. Defaults to Facebook Marketing.
            
        Returns:
            Role: The requested role configuration.
            
        Raises:
            ValueError: If the role type is not supported.
        """
        if not isinstance(role_type, RoleType):
            raise ValueError(f"Invalid role type: {role_type}. Must be a RoleType enum value.")
        
        return cls._ROLE_DEFINITIONS[role_type]
    
    @classmethod
    def get_role_by_name(cls, role_name: str) -> Optional[Role]:
        """
        Retrieve a role configuration by name (case-insensitive).
        
        Args:
            role_name: The name of the role to retrieve.
            
        Returns:
            Role: The requested role configuration, or None if not found.
        """
        if not role_name or not role_name.strip():
            return None
            
        try:
            role_type = RoleType(role_name.lower().strip())
            return cls.get_role(role_type)
        except ValueError:
            return None
    
    @classmethod
    def get_available_roles(cls) -> list[RoleType]:
        """
        Get a list of all available role types.
        
        Returns:
            list[RoleType]: List of available role types.
        """
        return list(cls._ROLE_DEFINITIONS.keys())
    
    @classmethod
    def get_role_names(cls) -> list[str]:
        """
        Get a list of all available role names.
        
        Returns:
            list[str]: List of role names.
        """
        return [role_type.value for role_type in cls._ROLE_DEFINITIONS.keys()]