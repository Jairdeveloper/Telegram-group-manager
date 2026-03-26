"""Errores específicos de la aplicación robot."""


class RobotError(Exception):
    """Error base para la aplicación robot."""
    pass


class ConfigurationError(RobotError):
    """Error de configuración."""
    pass


class TenantNotFoundError(RobotError):
    """Tenant no encontrado."""
    pass


class UserNotAuthorizedError(RobotError):
    """Usuario no autorizado."""
    pass


class RateLimitExceededError(RobotError):
    """Límite de rate exceeded."""
    pass


class PolicyViolationError(RobotError):
    """Violación de política."""
    pass


class InvalidUpdateError(RobotError):
    """Update inválido."""
    pass


class DuplicateUpdateError(RobotError):
    """Update duplicado."""
    pass


class ToolExecutionError(RobotError):
    """Error en ejecución de herramienta."""
    pass


class PlanExecutionError(RobotError):
    """Error en ejecución de plan."""
    pass


__all__ = [
    "RobotError",
    "ConfigurationError",
    "TenantNotFoundError",
    "UserNotAuthorizedError",
    "RateLimitExceededError",
    "PolicyViolationError",
    "InvalidUpdateError",
    "DuplicateUpdateError",
    "ToolExecutionError",
    "PlanExecutionError",
]
