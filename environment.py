class Environment:
    UNINITIALIZED = object()

    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        if name in self.values:
            raise RuntimeError(
                f"Variable '{name}' is already declared in this scope."
            )

        self.values[name] = value

    def declare(self, name):
        if name in self.values:
            raise RuntimeError(
                f"Variable '{name}' is already declared in this scope."
            )

        self.values[name] = self.UNINITIALIZED

    def initialize(self, name, value):
        if name not in self.values:
            raise RuntimeError(
                f"Variable '{name}' is not declared in this scope."
            )

        if self.values[name] is not self.UNINITIALIZED:
            raise RuntimeError(
                f"Variable '{name}' is already initialized."
            )

        self.values[name] = value

    def get(self, name):
        if name in self.values:
            value = self.values[name]

            if value is self.UNINITIALIZED:
                raise RuntimeError(
                    f"Cannot access '{name}' before initialization."
                )

            return value

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeError(f"Undefined variable '{name}'.")

    def assign(self, name, value):
        if name in self.values:
            if self.values[name] is self.UNINITIALIZED:
                raise RuntimeError(
                    f"Cannot assign to '{name}' before initialization."
                )

            self.values[name] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise RuntimeError(f"Undefined variable '{name}'.")