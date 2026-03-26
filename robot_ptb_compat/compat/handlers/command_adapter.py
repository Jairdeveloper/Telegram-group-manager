"""Adapter para comandos PTB."""

from typing import Any, Callable, List, Optional

from robot_ptb_compat.compat.handlers.base_adapter import BaseHandlerAdapter


class CommandAdapter(BaseHandlerAdapter):
    """Adaptador para CommandHandler de PTB."""
    
    def __init__(
        self,
        commands: List[str],
        callback: Callable,
        filters: Optional[Any] = None,
        pass_args: bool = False,
        pass_update_queue: bool = False,
        pass_job_queue: bool = False,
        pass_user_data: bool = True,
        pass_chat_data: bool = True,
        show_usage_in_inline_results: bool = True,
    ):
        """Inicializa el adaptador de comandos.
        
        Args:
            commands: Lista de comandos (sin/)
            callback: Función callback a ejecutar
            filters: Filtros PTB
            pass_args: Pasar argumentos del comando
            pass_update_queue: Pasar queue de updates
            pass_job_queue: Pasar job queue
            pass_user_data: Pasar user data
            pass_chat_data: Pasar chat data
            show_usage_in_inline_results: Mostrar uso en resultados inline
        """
        super().__init__(
            callback=callback,
            filters=filters,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
        )
        self.commands = [cmd.lower() for cmd in commands]
        self.pass_args = pass_args
    
    async def handle(self, update: Any, context: Any) -> Any:
        """Maneja el comando.
        
        Args:
            update: Update de Telegram
            context: Contexto del handler
            
        Returns:
            Resultado del callback
        """
        if not self.check_filter(update):
            return None
        
        message = update.message if hasattr(update, 'message') else None
        if not message or not message.text:
            return None
        
        text = message.text.strip()
        if not text.startswith('/'):
            return None
        
        parts = text[1:].split(maxsplit=1)
        command = parts[0].lower()
        
        if command not in self.commands:
            return None
        
        args = []
        if self.pass_args and len(parts) > 1:
            args = parts[1].split()
        
        context.args = args
        context.command = command
        
        return await self._execute_callback(update, context, *args)
    
    def get_commands(self) -> List[str]:
        """Retorna la lista de comandos.
        
        Returns:
            Lista de comandos
        """
        return self.commands
    
    def add_command(self, command: str) -> None:
        """Agrega un comando a la lista.
        
        Args:
            command: Comando a agregar
        """
        cmd = command.lower()
        if cmd not in self.commands:
            self.commands.append(cmd)


class CommandDispatcher:
    """Dispatcher para múltiples comandos."""
    
    def __init__(self):
        """Inicializa el dispatcher."""
        self._commands: dict[str, CommandAdapter] = {}
        self._default: Optional[Callable] = None
    
    def register(
        self,
        commands: List[str],
        callback: Callable,
        **kwargs
    ) -> CommandAdapter:
        """Registra un comando.
        
        Args:
            commands: Lista de comandos
            callback: Función callback
            **kwargs: Argumentos adicionales
            
        Returns:
            CommandAdapter creado
        """
        adapter = CommandAdapter(commands=commands, callback=callback, **kwargs)
        for cmd in adapter.get_commands():
            self._commands[cmd] = adapter
        return adapter
    
    def set_default(self, callback: Callable) -> None:
        """Define el handler por defecto.
        
        Args:
            callback: Función callback por defecto
        """
        self._default = callback
    
    async def dispatch(self, update: Any, context: Any) -> Any:
        """Dispara el comando apropiado.
        
        Args:
            update: Update de Telegram
            context: Contexto del handler
            
        Returns:
            Resultado del callback
        """
        message = update.message if hasattr(update, 'message') else None
        if not message or not message.text:
            return None
        
        text = message.text.strip()
        if not text.startswith('/'):
            return None
        
        parts = text[1:].split(maxsplit=1)
        command = parts[0].lower()
        
        adapter = self._commands.get(command)
        if adapter:
            return await adapter.handle(update, context)
        
        if self._default and self._default:
            return await self._default(update, context)
        
        return None
    
    def get_registered_commands(self) -> List[str]:
        """Retorna lista de comandos registrados.
        
        Returns:
            Lista de comandos
        """
        return list(self._commands.keys())


__all__ = ["CommandAdapter", "CommandDispatcher"]
