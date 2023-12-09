import logging
from hashlib import md5

from accounts.models import Account
from connectors.models import EventProcessingFilter, EventProcessingParser
from event.update_processor import event_processing_filter_update_processor, event_processing_parser_update_processor
from protos.event.stream_processing_pb2 import EventProcessingFilter as EventProcessingFilterProto, \
    UpdateEventProcessingFilterOp, EventProcessingParser as EventProcessingParserProto, UpdateEventProcessingParserOp
from utils.proto_utils import proto_to_dict

logger = logging.getLogger(__name__)


def get_or_create_event_processing_filter(scope: Account, event_processing_filter: EventProcessingFilterProto):
    which_one_of = event_processing_filter.WhichOneof('filter')
    db_filter = None
    if event_processing_filter.type == EventProcessingFilterProto.Type.DEFAULT:
        defaults = {'type': event_processing_filter.type, 'is_active': True}
        if event_processing_filter.name:
            defaults['name'] = event_processing_filter.name.value
    elif event_processing_filter.type == EventProcessingFilterProto.Type.REGEX and which_one_of == 'regex':
        defaults = {'type': EventProcessingFilterProto.Type.DEFAULT, 'is_active': True}
        db_filter = proto_to_dict(event_processing_filter.regex)
        if db_filter:
            defaults['type'] = event_processing_filter.type
            defaults['filter'] = db_filter
        if event_processing_filter.name:
            defaults['name'] = event_processing_filter.name.value
    else:
        return None
    try:
        if db_filter is not None and db_filter:
            db_filter_md5 = md5(str(db_filter).encode('utf-8')).hexdigest()
            saved_event_processing_filter, _ = EventProcessingFilter.objects.get_or_create(account_id=scope.id,
                                                                                           filter_md5=db_filter_md5,
                                                                                           defaults=defaults)
        else:
            saved_event_processing_filter, _ = EventProcessingFilter.objects.get_or_create(account_id=scope.id,
                                                                                           defaults=defaults)

        if saved_event_processing_filter:
            return saved_event_processing_filter
    except Exception as e:
        logger.error(f"Exception occurred while saving event processing filter with error: {e}")
    return None


def update_or_create_event_processing_filter(scope: Account, event_processing_filter_id,
                                             update_event_processing_filter_ops: [UpdateEventProcessingFilterOp]):
    try:
        account_event_processing_filter = scope.eventprocessingfilter_set.get(id=event_processing_filter_id)
        return event_processing_filter_update_processor.update(account_event_processing_filter,
                                                               update_event_processing_filter_ops)
    except EventProcessingFilter.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Exception occurred while updating event processing filter with error: {e}")
        return None


def get_or_create_event_processing_parser(scope: Account, event_processing_parsers: [EventProcessingParserProto]):
    if not scope:
        logger.error(f"Scope not found for event processing parser create request")
        return None
    saved_event_processing_parsers = []
    for parser in event_processing_parsers:
        drd_event_definition_rule = proto_to_dict(parser.drd_event_definition_rule)
        if not drd_event_definition_rule:
            logger.error(f"DRD event definition rule not found in event processing parser definition")
            continue
        which_one_of = parser.WhichOneof('parser')
        if not parser.filter.id or not parser.filter.id.value:
            logger.error(f"Filter id not found in event processing parser definition")
            continue
        filter_id = parser.filter.id.value
        parser_type = EventProcessingParserProto.Type.DEFAULT
        drd_event_definition_rule_md5 = md5(str(drd_event_definition_rule).encode('utf-8')).hexdigest()
        defaults = {'type': parser_type, 'is_active': True, 'drd_event_definition_rule': drd_event_definition_rule}
        parser_rule = None
        if parser.name:
            defaults['name'] = parser.name.value
        if parser.type == EventProcessingParserProto.Type.GROK and which_one_of == 'grok_parser':
            parser_rule = proto_to_dict(parser.grok_parser)
            if parser_rule:
                defaults['type'] = parser.type
                defaults['parser'] = parser_rule
        try:
            if parser_rule is not None and parser_rule:
                parser_rule_md5 = md5(str(parser).encode('utf-8')).hexdigest()
                saved_event_processing_parser, _ = EventProcessingParser.objects.get_or_create(account_id=scope.id,
                                                                                               parser_md5=parser_rule_md5,
                                                                                               drd_event_definition_rule_md5=drd_event_definition_rule_md5,
                                                                                               filter_id=filter_id,
                                                                                               defaults=defaults)
            else:
                saved_event_processing_parser, _ = EventProcessingParser.objects.get_or_create(account_id=scope.id,
                                                                                               drd_event_definition_rule_md5=drd_event_definition_rule_md5,
                                                                                               filter_id=filter_id,
                                                                                               defaults=defaults)
            if saved_event_processing_parser:
                saved_event_processing_parsers.append(saved_event_processing_parser)
        except Exception as e:
            logger.error(f"Exception occurred while saving event processing parser with error: {e}")
            continue
    return saved_event_processing_parsers


def update_or_create_event_processing_parser(scope: Account, event_processing_parser_id,
                                             update_event_processing_parser_ops: [UpdateEventProcessingParserOp]):
    try:
        account_event_processing_filter = scope.eventprocessingparser_set.get(id=event_processing_parser_id)
        return event_processing_parser_update_processor.update(account_event_processing_filter,
                                                               update_event_processing_parser_ops)
    except EventProcessingParser.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Exception occurred while updating event processing parser with error: {e}")
        return None


def get_or_create_event_processing_filter_parsers(scope: Account,
                                                  event_processing_parsers: [EventProcessingParserProto]):
    saved_event_processing_parsers = []
    for parser in event_processing_parsers:
        drd_event_definition_rule = proto_to_dict(parser.drd_event_definition_rule)
        event_processing_filter = parser.filter
        if not drd_event_definition_rule:
            logger.error(f"DRD event definition rule not found in event processing parser definition")
            continue
        which_one_of = event_processing_filter.WhichOneof('filter')
        db_filter = None
        if event_processing_filter.type == EventProcessingFilterProto.Type.DEFAULT:
            defaults = {'type': event_processing_filter.type, 'is_active': True}
        elif event_processing_filter.type == EventProcessingFilterProto.Type.REGEX and which_one_of == 'regex':
            defaults = {'type': EventProcessingFilterProto.Type.DEFAULT, 'is_active': True}
            db_filter = proto_to_dict(event_processing_filter.regex)
            if db_filter:
                defaults['type'] = event_processing_filter.type
                defaults['filter'] = db_filter
        else:
            logger.error(f"Event processing filter type not found in event processing parser definition")
            continue
        if event_processing_filter.name:
            defaults['name'] = event_processing_filter.name.value
        try:
            if db_filter is not None and db_filter:
                db_filter_md5 = md5(str(db_filter).encode('utf-8')).hexdigest()
                saved_event_processing_filter, _ = EventProcessingFilter.objects.get_or_create(account_id=scope.id,
                                                                                               filter_md5=db_filter_md5,
                                                                                               defaults=defaults)
            else:
                saved_event_processing_filter, _ = EventProcessingFilter.objects.get_or_create(account_id=scope.id,
                                                                                               defaults=defaults)
        except Exception as e:
            logger.error(
                f"Exception occurred while saving event processing filter for parser create request with error: {e}")
            continue
        if not saved_event_processing_filter:
            logger.error(f"Event processing filter not found for parser create request")
            continue
        else:
            which_one_of = parser.WhichOneof('parser')
            filter_id = saved_event_processing_filter.id
            parser_type = EventProcessingParserProto.Type.DEFAULT
            drd_event_definition_rule_md5 = md5(str(drd_event_definition_rule).encode('utf-8')).hexdigest()
            defaults = {'type': parser_type, 'is_active': True,
                        'drd_event_definition_rule': drd_event_definition_rule}
            parser_rule = None
            if parser.name:
                defaults['name'] = parser.name.value
            if parser.type == EventProcessingParserProto.Type.GROK and which_one_of == 'grok_parser':
                parser_rule = proto_to_dict(parser.grok_parser)
                if parser_rule:
                    defaults['type'] = parser.type
                    defaults['parser'] = parser_rule
            try:
                if parser_rule is not None and parser_rule:
                    parser_rule_md5 = md5(str(parser).encode('utf-8')).hexdigest()
                    saved_event_processing_parser, _ = EventProcessingParser.objects.get_or_create(
                        account_id=scope.id,
                        parser_md5=parser_rule_md5,
                        drd_event_definition_rule_md5=drd_event_definition_rule_md5,
                        filter_id=filter_id,
                        defaults=defaults)
                else:
                    saved_event_processing_parser, _ = EventProcessingParser.objects.get_or_create(
                        account_id=scope.id,
                        drd_event_definition_rule_md5=drd_event_definition_rule_md5,
                        filter_id=filter_id,
                        defaults=defaults)
                if saved_event_processing_parser:
                    saved_event_processing_parsers.append(saved_event_processing_parser)
            except Exception as e:
                logger.error(
                    f"Exception occurred while saving event processing parser for parser create request with error: {e}")
                continue
    return saved_event_processing_parsers
