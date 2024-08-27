my_dict = {
    "context": ["plate/sv4ks100/exr", "plate/fh/exr", "plate/wh/exr", "compplate/wh/exr"],
    "category": ["bg", "pl", "el", "cp", ""],
    "number": ["01", ""],
    "descriptor": ["dn_rt", "", "dn", "rt", "dn_pm", "pm", "flat", "flop"],
}

keys = list(my_dict.keys())


for item2 in my_dict[keys[1]]:
    for item3 in my_dict[keys[2]]:
        for item4 in my_dict[keys[3]]:
            pass
            # print(f"{item2}{item3}_{item4}")


keys = list(my_dict.keys())


def walk(key_idx=1, current_str=""):
    if key_idx == len(keys):
        yield current_str
        return
    for item in my_dict[keys[key_idx]]:
        if key_idx == 3 and current_str and item:
            item = f"_{item}"
        new_str = current_str + item
        yield from walk(key_idx + 1, new_str)


# Start the recursion with the second key ('category') since 'context' is not used in the combinations.
for path in walk():
    print(path)
