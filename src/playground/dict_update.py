import dataclasses
import functools

# import nuke


def keep_selected(func):
    """Decorator to keep the selected nodes after the function is called.

    Args:
        func (callable): The function to decorate.

    Returns:
        callable: The decorated function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Save the current selection
        # current_selection = nuke.selectedNodes()
        # Call the function
        try:
            result = func(*args, **kwargs)
        finally:
            pass
            # Restore the selection
            # set_selected(current_selection)
        return result  # type: ignore

    return wrapper  # type: ignore


def decorator_wrap_test(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # -> Any:

        try:
            results = func(*args, **kwargs)
        finally:
            print("Results", results)

        return results

    return wrapper


@dataclasses.dataclass
class Test:
    name: str = dataclasses.field(default="Test")
    code: str = dataclasses.field(default="Code")
    overscan: list = dataclasses.field(default_factory=list)


@keep_selected
def keep_type() -> Test:

    test_item = Test()

    return test_item


if __name__ == "__main__":
    my_test = keep_type()
    print(my_test)
