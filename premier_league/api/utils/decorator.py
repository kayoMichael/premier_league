import os
from functools import wraps

from flask import after_this_request, current_app, g


def safe_file_cleanup(func):
    """
    A decorator that ensures temporary files are properly cleaned up after a Flask request,
    whether the request succeeds or fails. The decorated function must store the file path
    in g.temp_state['file_path'].

    This decorator handles file cleanup in two scenarios:
    1. After a successful request completion (using Flask's after_this_request)
    2. Immediately if an exception occurs during request processing

    Args:
        func: The Flask route function to be decorated

    Returns:
        wrapper: The decorated function that includes file cleanup logic
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        file_path = None
        try:
            result = func(*args, **kwargs)
            file_path = g.temp_state.get("file_path")
            print(file_path)

            @after_this_request
            def cleanup(response):
                try:
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                        current_app.logger.info(
                            f"Successfully deleted file: {file_path}"
                        )
                    if os.path.exists("files") and any(os.scandir("files")):
                        os.removedirs("files")
                        current_app.logger.info(
                            f"Cleaned up directory after error: files"
                        )
                except Exception as e:
                    current_app.logger.error(
                        f"Error deleting file {file_path}: {str(e)}"
                    )
                return response

            return result

        except Exception as e:
            # Clean up file and directory if something went wrong before sending
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    current_app.logger.info(f"Cleaned up file after error: {file_path}")
                except Exception as cleanup_error:
                    current_app.logger.error(
                        f"Error during cleanup: {str(cleanup_error)}"
                    )
            if os.path.exists("files") and any(os.scandir("files")):
                os.removedirs("files")
                current_app.logger.info(f"Cleaned up directory after error: files")
            raise e

    return wrapper
