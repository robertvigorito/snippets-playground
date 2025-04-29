# Original number
import math

num = 2.15262776e17

# Format to 2.15 (three significant figures)
formatted_num = float(f"{num:.2g}".split("e")[0])

print(formatted_num)
