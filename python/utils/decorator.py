import functools
from typing import Callable, Union, get_args, Any

def singleton(cls):
    """
    Decorator to create a singleton class.

    Ensures that only one instance of the decorated class is created.

    This implementation uses a class decorator and leverages the `__init__` method
    to initialize the instance only once.

    Example:
        >>> @singleton
        ... class MyClass:
        ...     pass
        >>> instance1 = MyClass()
        >>> instance2 = MyClass()
        >>> instance1 is instance2
        True
    """
    _instance = None

    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        nonlocal _instance
        if _instance is None:
            _instance = cls(*args, **kwargs)
        return _instance

    return wrapper


def cmd_arg_converter(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        arguments: list[Any] = list(args)
        annotations: list[Any] = [v for k, v in func.__annotations__.items() if k != "return" and k != "player"]

        converted_args: list[Any] = [arguments.pop(0)]
        annotation_len: int = len(annotations)

        for i, arg in enumerate(arguments[:annotation_len]):
            annotation = annotations[i]

            if isinstance(annotation, type(Union[int, str])):
                for t in get_args(annotation):
                    try:
                        converted_args.append(t(arg))
                        break
                    except:
                        pass
                else:
                    raise ValueError(f"Cannot convert '{arg}' to any type in {annotation} for {func.__name__}")
                continue

            try: 
                converted_args.append(annotation(arg))
            except:
                converted_args.append(arg)

        converted_args.extend(args[annotation_len + 1:])
        print(converted_args)

        return func(*converted_args, **kwargs)
    return wrapper