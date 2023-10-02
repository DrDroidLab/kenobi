class ProcessorError(ValueError):
    pass


class KeyDeserializationError(ProcessorError):
    pass


class ValueDeserializationError(ProcessorError):
    pass


class Processor:
    key_cls = None
    value_cls = None

    def transform(self, key, value):
        try:
            proto_key = self.key_cls()
            proto_key.ParseFromString(key)
        except Exception as e:
            raise KeyDeserializationError(f'{e} error deserializing key to message type {self.key_cls}')

        try:
            proto_value = self.value_cls()
            proto_value.ParseFromString(value)
        except Exception as e:
            raise ValueDeserializationError(f'{e} error deserializing value to message type {self.value_cls}')

        return proto_key, proto_value

    def process(self, keys, values):
        pass


class ConsoleProcessor(Processor):
    def process(self, keys, values):
        for key, value in zip(keys, values):
            print(key, value)
