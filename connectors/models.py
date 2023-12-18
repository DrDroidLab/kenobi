from datetime import timezone
from hashlib import md5

from django.db import models
from google.protobuf.wrappers_pb2 import StringValue, BoolValue, UInt64Value

from accounts.models import Account
from protos.event.connectors_pb2 import ConnectorKey as ConnectorKeyProto, PeriodicRunStatus, ConnectorType, \
    TransformerType, DecoderType
from protos.event.stream_processing_pb2 import EventProcessingFilter as EventProcessingFilterProto, \
    RegexEventProcessingFilter, EventProcessingParser as EventProcessingParserProto, GrokEventProcessingParser

from utils.model_utils import generate_choices
from utils.proto_utils import dict_to_proto


class Connector(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=255)
    connector_type = models.IntegerField(null=True, blank=True, choices=generate_choices(ConnectorType),
                                         default=ConnectorType.UNKNOWN)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = [['account', 'name', 'connector_type']]

    def __str__(self):
        return f'{self.account}:{self.connector_type}'


class ConnectorKey(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    key_type = models.IntegerField(null=True, blank=True,
                                   choices=generate_choices(ConnectorKeyProto.KeyType))
    key = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = [['account', 'connector', 'key_type', 'key']]

    def get_proto(self):
        return ConnectorKeyProto(key_type=self.key_type,
                                 key=StringValue(value=self.key),
                                 is_active=BoolValue(value=self.is_active))


class ConnectorPeriodicRunMetadata(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    metadata = models.JSONField()
    task_run_id = models.CharField(max_length=255)
    status = models.IntegerField(null=True, blank=True,
                                 choices=generate_choices(PeriodicRunStatus.StatusType))
    started_at = models.DateTimeField(blank=True, null=True, db_index=True)
    finished_at = models.DateTimeField(blank=True, null=True, db_index=True)


class ConnectorRequest(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)
    connector_type = models.IntegerField(null=True, blank=True, choices=generate_choices(ConnectorType),
                                         default=ConnectorType.UNKNOWN)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = [['account', 'connector_type']]


class TransformerMapping(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)
    decoder_type = models.IntegerField(null=True, blank=True, choices=generate_choices(DecoderType),
                                       default=DecoderType.UNKNOWN_DT)
    transformer_type = models.IntegerField(null=True, blank=True, choices=generate_choices(TransformerType),
                                           default=TransformerType.UNKNOWN_TT)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = [['account', 'decoder_type', 'transformer_type']]


class EventProcessingFilter(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    type = models.IntegerField(null=True, blank=True, choices=generate_choices(EventProcessingFilterProto.Type),
                               default=EventProcessingFilterProto.Type.DEFAULT)
    filter = models.JSONField(null=True, blank=True)
    filter_md5 = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = [['account', 'type', 'filter_md5']]

    def __str__(self):
        return f'{self.account}:{self.type}:{self.filter}'

    def save(self, **kwargs):
        if self.filter:
            self.filter_md5 = md5(str(self.filter).encode('utf-8')).hexdigest()
        super().save(**kwargs)

    @property
    def proto(self) -> EventProcessingFilterProto:
        if self.type == EventProcessingFilterProto.Type.DEFAULT:
            if self.name:
                return EventProcessingFilterProto(id=UInt64Value(value=self.id),
                                                  name=StringValue(value=str(self.name)),
                                                  type=self.type,
                                                  is_active=BoolValue(value=self.is_active),
                                                  created_at=int(
                                                      self.created_at.replace(tzinfo=timezone.utc).timestamp()
                                                  ))
            else:
                return EventProcessingFilterProto(id=UInt64Value(value=self.id),
                                                  type=self.type,
                                                  is_active=BoolValue(value=self.is_active),
                                                  created_at=int(
                                                      self.created_at.replace(tzinfo=timezone.utc).timestamp()
                                                  ))
        elif self.type == EventProcessingFilterProto.Type.REGEX:
            event_processing_filter_proto = dict_to_proto(self.filter, RegexEventProcessingFilter)
            if event_processing_filter_proto:
                if self.name:
                    return EventProcessingFilterProto(id=UInt64Value(value=self.id),
                                                      name=StringValue(value=str(self.name)),
                                                      type=self.type,
                                                      regex=event_processing_filter_proto,
                                                      is_active=BoolValue(value=self.is_active),
                                                      created_at=int(
                                                          self.created_at.replace(tzinfo=timezone.utc).timestamp()
                                                      ))
                else:
                    return EventProcessingFilterProto(id=UInt64Value(value=self.id),
                                                      type=self.type,
                                                      regex=event_processing_filter_proto,
                                                      is_active=BoolValue(value=self.is_active),
                                                      created_at=int(
                                                          self.created_at.replace(tzinfo=timezone.utc).timestamp()
                                                      ))
        return EventProcessingFilterProto()


class EventProcessingParser(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)
    filter = models.ForeignKey(EventProcessingFilter, on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    type = models.IntegerField(null=True, blank=True, choices=generate_choices(EventProcessingParserProto.Type),
                               default=EventProcessingParserProto.Type.DEFAULT)
    parser = models.JSONField(null=True, blank=True, db_index=True)
    parser_md5 = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    drd_event_definition_rule = models.JSONField(null=True, blank=True, db_index=True)
    drd_event_definition_rule_md5 = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = [['account', 'type', 'filter', 'parser_md5', 'drd_event_definition_rule_md5']]

    def __str__(self):
        return f'{self.account}:{self.type}:{self.parser}'

    def save(self, **kwargs):
        if self.parser:
            self.parser_md5 = md5(str(self.parser).encode('utf-8')).hexdigest()
        if self.drd_event_definition_rule:
            self.drd_event_definition_rule_md5 = md5(str(self.drd_event_definition_rule).encode('utf-8')).hexdigest()
        super().save(**kwargs)

    @property
    def proto(self) -> EventProcessingParserProto:
        filter_proto = self.filter.proto
        drd_event_definition_rule_proto = dict_to_proto(self.drd_event_definition_rule,
                                                        EventProcessingParserProto.ParsedDrdEventDefinition)
        if self.type == EventProcessingParserProto.Type.DEFAULT:
            return EventProcessingParserProto(id=UInt64Value(value=self.id),
                                              name=StringValue(value=str(self.name)),
                                              type=self.type,
                                              filter=filter_proto,
                                              drd_event_definition_rule=drd_event_definition_rule_proto,
                                              is_active=BoolValue(value=self.is_active),
                                              created_at=int(self.created_at.replace(tzinfo=timezone.utc).timestamp()))
        elif self.type == EventProcessingParserProto.Type.GROK:
            grok_parser_proto = dict_to_proto(self.parser, GrokEventProcessingParser)
            return EventProcessingParserProto(id=UInt64Value(value=self.id),
                                              name=StringValue(value=str(self.name)),
                                              type=self.type,
                                              filter=filter_proto,
                                              drd_event_definition_rule=drd_event_definition_rule_proto,
                                              is_active=BoolValue(value=self.is_active),
                                              created_at=int(self.created_at.replace(tzinfo=timezone.utc).timestamp()),
                                              grok_parser=grok_parser_proto)

        return EventProcessingParserProto()