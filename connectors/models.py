from django.db import models
from google.protobuf.wrappers_pb2 import StringValue, BoolValue

from accounts.models import Account
from protos.event.connectors_pb2 import ConnectorKey as ConnectorKeyProto, PeriodicRunStatus, ConnectorType, \
    TransformerType, DecoderType

from utils.model_utils import generate_choices


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
