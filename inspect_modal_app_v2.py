import modal
import inspect

app = modal.App("test")
sig = inspect.signature(app.function)
print("Arguments for app.function:")
for name, param in sig.parameters.items():
    print(f" - {name}")

try:
    import modal.version
    print(f"Modal version: {modal.version.__version__}")
except:
    pass
