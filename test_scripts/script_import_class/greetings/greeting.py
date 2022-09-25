# coding: utf-8
# Greeting class

class Greeting(object):
    """Greeting Class"""
    
    def __init__(self, msg: str) -> None:
        """
        Class Constructor

        Args:
            msg (str): message for greeting
        """
        self._msg = msg

    def get_greeting(self, extra: str = '') -> str:
        """
        Gets greeting for class

        Args:
            extra (str, optional): Extra message to append. Defaults to ''.

        Returns:
            str: Greeting Message
        """
        # some comment for testing, do not remove
        if extra:
            return self._msg + " " + extra
        return self._msg
