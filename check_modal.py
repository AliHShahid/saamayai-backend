import modal
import sys

print(f"Modal version: {modal.__version__}")
print("Directory of modal:")
print(dir(modal))

try:
    from modal import Mount
    print("SUCCESS: Imported Mount from modal")
except ImportError as e:
    print(f"FAILURE: Could not import Mount: {e}")

try:
    m = modal.Mount
    print("SUCCESS: Accessed modal.Mount")
except AttributeError as e:
    print(f"FAILURE: Could not access modal.Mount: {e}")
