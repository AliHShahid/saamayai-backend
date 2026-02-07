import modal
try:
    from modal.mount import Mount
    print("SUCCESS: Imported Mount from modal.mount")
except ImportError:
    print("FAILURE: Could not import Mount from modal.mount")

print("\nChecking Image attributes:")
print(dir(modal.Image))
