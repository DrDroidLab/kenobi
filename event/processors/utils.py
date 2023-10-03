from protos.event.base_pb2 import EventKey as EventKeyProto
from protos.event.schema_pb2 import Value


def infer_key_type(v: Value):
    which_one_of = v.WhichOneof('value')
    if which_one_of == 'string_value':
        return EventKeyProto.KeyType.STRING
    elif which_one_of == 'int_value':
        return EventKeyProto.KeyType.LONG
    elif which_one_of == 'double_value':
        return EventKeyProto.KeyType.DOUBLE
    elif which_one_of == 'bool_value':
        return EventKeyProto.KeyType.BOOLEAN
    elif which_one_of == 'byte_value':
        return EventKeyProto.KeyType.BYTE
    elif which_one_of == 'array_value':
        return EventKeyProto.KeyType.ARRAY
    elif which_one_of == 'kvlist_value':
        return EventKeyProto.KeyType.OBJECT
    return EventKeyProto.KeyType.UNKNOWN
