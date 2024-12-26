from llvmlite import ir
from typing import Optional


class Environment:
    def __init__(
        self,
        records: dict[str, tuple[ir.Value, ir.Type]] = None,
        parent=None,
        name: str = "global",
    ):
        self.__records = records if records else {}
        self.parent: Environment = parent
        self.name: str = name

    def define(self, name: str, value: ir.Value, identifier_type: ir.Type) -> ir.Value:
        self.__records[name] = (value, identifier_type)
        return value

    def lookup(self, name: str) -> tuple[ir.Value, ir.Type]:
        return self.__resolve(name)

    def __resolve(self, name: str) -> Optional[tuple[ir.Value, ir.Type]]:
        if name in self.__records:
            return self.__records[name]

        elif self.parent:
            self.parent.__resolve(name)
        else:
            return None
