import os
from flask import after_this_request, current_app, g
from functools import wraps


def safe_file_cleanup(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        file_path = None
        try:
            result = func(*args, **kwargs)
            file_path = g.temp_state.get('file_path')
            print(file_path)

            @after_this_request
            def cleanup(response):
                try:
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                        current_app.logger.info(f"Successfully deleted file: {file_path}")
                except Exception as e:
                    current_app.logger.error(f"Error deleting file {file_path}: {str(e)}")
                return response

            return result

        except Exception as e:
            # Clean up file if something went wrong before sending
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    current_app.logger.info(f"Cleaned up file after error: {file_path}")
                except Exception as cleanup_error:
                    current_app.logger.error(f"Error during cleanup: {str(cleanup_error)}")
            raise e

    return wrapper
