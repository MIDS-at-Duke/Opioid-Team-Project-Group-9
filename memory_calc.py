# Checking available memory to ascertain chunksize

import psutil

# Get the memory details
memory_info = psutil.virtual_memory()

# Print the available memory
print(f"Available memory: {memory_info.available / (1024.0 ** 3)} GB")

# Available memory: 31.999996185302734 GB
