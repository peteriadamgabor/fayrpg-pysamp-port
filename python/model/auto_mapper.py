class AutoMapper:
    def __init__(self):
        self.mappings = {}

    def add_mapping(self, source_class, destination_class, custom_mappings=None):
        """Add a mapping configuration between source and destination classes."""
        self.mappings[(source_class, destination_class)] = custom_mappings or {}

    def map(self, source, destination_class):
        """Map the source object or dictionary to an instance of destination_class."""
        mapping_key = (type(source), destination_class)
        custom_mappings: dict[str, str] = self.mappings.get(mapping_key, {})

        # Generate the data for the destination class
        destination_data = {}

        for key in destination_class.__annotations__:
            if isinstance(source, dict):
                # If source is a dictionary, use the key directly
                if key in source:
                    destination_data[key] = source[key]
            else:
                # If source is an object, use getattr
                if hasattr(source, key):
                    destination_data[key] = getattr(source, key)

        # Apply custom mappings if any
        if custom_mappings:
            for dest_field, source_field in custom_mappings.items():
                if isinstance(source, dict):
                    destination_data[dest_field] = source.get(source_field)
                else:
                    if hasattr(source, source_field):
                        destination_data[dest_field] = getattr(source, source_field)

        return destination_class(**destination_data)