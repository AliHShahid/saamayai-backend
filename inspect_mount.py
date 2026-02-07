from modal.mount import Mount
import inspect

print("Is 'from_local_dir' in dir(Mount)?", 'from_local_dir' in dir(Mount))
print("Is 'add_local_dir' in dir(Mount)?", 'add_local_dir' in dir(Mount))

try:
    print("Mount.add_local_dir type:", type(Mount.add_local_dir))
except:
    pass

try:
    print("Mount._from_local_dir type:", type(Mount._from_local_dir))
except:
    pass
