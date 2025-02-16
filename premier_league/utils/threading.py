import inspect
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from typing import Callable, List, Optional, TypeVar

from tqdm import tqdm

T = TypeVar("T")


def run_threaded(
    func: Callable[..., T],
    items: List[any],
    desc: str = "Processing",
    unit: str = "items",
    max_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
    show_progress: bool = False,
) -> List[T]:
    """
    Runs a function across multiple items using thread pooling.

    Args:
        func: The function to run on each item
        items: List of items to process
        desc: The description for the progress bar
        unit: The unit for the progress bar
        max_workers: Number of thread workers (defaults to min(32, cpu_count + 4))
        chunk_size: Size of chunks for map
        show_progress: Whether to show progress bar using tqdm

    Returns:
        List of results in the same order as input items
    """
    total_items = len(items)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        if show_progress:
            with tqdm(total=total_items, desc=desc, unit=unit) as pbar:
                results = []
                for result in executor.map(func, items, chunksize=chunk_size):
                    results.append(result)
                    pbar.update(1)
        else:
            results = list(executor.map(func, items, chunksize=chunk_size))

    return results


def threaded(
    max_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
    desc: Optional[str] = None,
    unit: Optional[str] = None,
    show_progress: Optional[bool] = False,
) -> Callable:
    """
    Decorator to make any function run in threaded mode when given a list input.

    Args:
        max_workers: Number of thread workers
        chunk_size: Size of chunks for map
        show_progress: Whether to show progress bar
        desc: Description for the progress bar
        unit: Unit for the progress bar
    """

    def decorator(func: Callable[..., T]) -> Callable[..., List[T]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> List[T]:
            self_arg = args[0] if args and hasattr(args[0], "__class__") else None
            items = args[1] if len(args) > 1 else kwargs.pop("items", None)

            if items is None:
                raise ValueError(
                    "Threaded decorator requires an iterable as the first argument after 'self'"
                )

            decorator_kwargs = {
                "max_workers": kwargs.pop("max_workers", max_workers),
                "chunk_size": kwargs.pop("chunk_size", chunk_size),
                "show_progress": kwargs.pop("show_progress", show_progress),
                "desc": kwargs.pop("desc", desc),
                "unit": kwargs.pop("unit", unit),
            }

            if not isinstance(items, list):
                items = [items]

            def wrapped_func(item):
                func_signature = inspect.signature(func)
                valid_kwargs = {
                    k: v for k, v in kwargs.items() if k in func_signature.parameters
                }

                if self_arg:
                    return func(self_arg, item, **valid_kwargs)
                return func(item, **valid_kwargs)

            return run_threaded(
                wrapped_func,
                items,
                desc=decorator_kwargs["desc"] or "processing",
                unit=decorator_kwargs["unit"] or "items",
                max_workers=decorator_kwargs["max_workers"],
                chunk_size=decorator_kwargs["chunk_size"],
                show_progress=decorator_kwargs["show_progress"],
            )

        return wrapper

    return decorator
