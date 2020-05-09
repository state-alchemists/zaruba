from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Type, Any
from logging import Logger

Message = Dict[str, Any]
RPCHandler = Callable[..., Any]
EventHandler = Callable[[Message], None]


class RPCClient(ABC):

    @abstractmethod
    def call(self, function_name: str, *inputs: Any) -> Any:
        pass

    @abstractmethod
    def set_logger(self, logger: Logger) -> RPCClient:
        pass


class RPCServer(ABC):

    @abstractmethod
    def register_handler(self, function_name: str, handler: RPCHandler) -> RPCServer:
        pass

    @abstractmethod
    def set_logger(self, logger: Logger) -> RPCServer:
        pass

    @abstractmethod
    def serve(self) -> None:
        pass


class Publisher(ABC):

    @abstractmethod
    def publish(self, event_name: str, msg: Message):
        pass

    @abstractmethod
    def set_logger(self, logger: Logger) -> Publisher:
        pass


class Subscriber(ABC):

    @abstractmethod
    def register_handler(self, event_name: str, handler: EventHandler) -> Subscriber:
        pass

    @abstractmethod
    def set_logger(self, logger: Logger) -> Subscriber:
        pass

    @abstractmethod
    def subscribe(self) -> None:
        pass
