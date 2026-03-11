"""Module registry for ManagerBot."""

from typing import Any, Callable, Dict, List, Optional

from app.manager_bot.core import Module


class ModuleRegistry:
    """Registro central de módulos del ManagerBot."""

    def __init__(self):
        self._modules: Dict[str, Module] = {}

    def register(self, module: Module) -> None:
        """Registrar módulo con su feature flag."""
        if module.contract.name in self._modules:
            raise ValueError(
                f"Module '{module.contract.name}' is already registered"
            )
        self._modules[module.contract.name] = module

    def get_module(self, name: str) -> Optional[Module]:
        """Obtener módulo por nombre."""
        return self._modules.get(name)

    def is_enabled(self, name: str) -> bool:
        """Verificar si un módulo está habilitado."""
        module = self._modules.get(name)
        return module.is_enabled() if module else False

    def list_modules(self) -> List[str]:
        """Listar todos los módulos registrados."""
        return list(self._modules.keys())

    def list_enabled_modules(self) -> List[Module]:
        """Listar solo módulos habilitados."""
        return [
            module for module in self._modules.values() if module.is_enabled()
        ]

    def get_all_handlers(self) -> Dict[str, Callable]:
        """Obtener todos los handlers de módulos habilitados."""
        handlers = {}
        for module in self.list_enabled_modules():
            module_handlers = module.get_handlers()
            handlers.update(module_handlers)
        return handlers

    def unregister(self, name: str) -> None:
        """Desregistrar un módulo."""
        if name in self._modules:
            del self._modules[name]
