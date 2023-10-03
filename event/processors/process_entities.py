from google.protobuf.wrappers_pb2 import UInt64Value, StringValue

from accounts.models import Account
from event.models import EntityInstanceEventMapping
from protos.kafka.base_pb2 import DiscoveredEntityInstance


def process_event_entities(account: Account, event_key_id_set, saved_events, event_key_dict_list):
    eiems = []
    event_entity_instance_lists = [[]] * len(saved_events)
    entity_event_keys = list(account.entityeventkeymapping_set.filter(
        is_active=True, entity__is_active=True, event_key_id__in=event_key_id_set
    ).values('entity_id', 'event_key_id'))
    if entity_event_keys:
        event_entity_instance_lists = []
        for idx, (saved_event, event_key_dict) in enumerate(zip(saved_events, event_key_dict_list)):
            event_keys = event_key_dict.keys()

            event_entity_instance_list = []
            for entity_event_key in entity_event_keys:
                entity_id = entity_event_key['entity_id']
                event_key_id = entity_event_key['event_key_id']

                if event_key_id in event_keys:
                    instance_value = str(event_key_dict[event_key_id])
                    instance, _ = account.entityinstance_set.get_or_create(
                        entity_id=entity_id, instance=instance_value
                    )
                    eiem = EntityInstanceEventMapping(
                        account=account,
                        entity_instance=instance,
                        event=saved_event,
                        event_key_id=event_key_id,
                        entity_id=entity_id,
                        instance=instance_value,
                        event_processed_kvs=saved_event.processed_kvs,
                        event_timestamp=saved_event.timestamp,
                    )
                    eiems.append(eiem)
                    event_entity_instance_list.append({
                        'entity_instance_id': instance.id, 'entity_id': entity_id, 'instance': instance_value
                    })
            event_entity_instance_lists.append(event_entity_instance_list)

    if eiems:
        EntityInstanceEventMapping.objects.bulk_create(eiems, batch_size=25)

    return event_entity_instance_lists


def get_discovered_entity_instance_lists(account_id, event_entity_instance_lists):
    return [
        [
            DiscoveredEntityInstance(
                account_id=UInt64Value(value=account_id),
                entity_instance_id=UInt64Value(value=entity_instance['entity_instance_id']),
                entity_id=UInt64Value(value=entity_instance['entity_id']),
                instance=StringValue(value=entity_instance['instance']),
            ) for entity_instance in entity_instance_list
        ]
        for entity_instance_list in event_entity_instance_lists
    ]
