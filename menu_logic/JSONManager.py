import json as js

class JSONManager:
    """A utility class for handling JSON file operations such as reading, writing, and updating JSON data."""

    @staticmethod
    def read_json(file_path):
        """Reads a JSON file and returns its content as a Python dictionary."""
        with open(file_path, 'r') as file:
            return js.load(file)
    
    @staticmethod
    def write_json(file_path, data):
        """
        Writes a Python dictionary to a JSON file with pretty formatting.

        :param file_path: The path to the JSON file to write to.

        :param data: The Python dictionary to write to the JSON file.
        """
        with open(file_path, 'w') as file:
            js.dump(data, file, indent=4)

    @staticmethod
    def update_json(file_path, key, value):
        """
        Updates a specific key-value pair in a JSON file. If the key does not exist, it will be added.

        :param file_path: The path to the JSON file to update.

        :param key: The key to update or add in the JSON file.
        
        :param value: The value to set for the specified key in the JSON file.
        """


        data = JSONManager.read_json(file_path)
        data[key] = value
        JSONManager.write_json(file_path, data)