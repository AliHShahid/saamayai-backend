import modal
app = modal.App("test")

print("App.function arguments:")
import inspect
try:
    print(inspect.signature(app.function))
except Exception as e:
    print(f"Error inspecting: {e}")

# Also check modal version if possible
try:
    import modal.version
    print(f"Modal version: {modal.version.__version__}")
except:
    pass
