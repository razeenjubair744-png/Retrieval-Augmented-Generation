import builtins
import uuid
builtins.uuid = uuid

print("Success: uuid injected into builtins. uuid.uuid4() works:", builtins.uuid.uuid4())
