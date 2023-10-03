from django.db.utils import IntegrityError
from google.protobuf.wrappers_pb2 import BoolValue, StringValue

from accounts.models import Account
from event.models import Monitor
from event.update_processor import monitor_update_processor
from protos.event.api_pb2 import CreateOrUpdateMonitorRequest, Message, CreateOrUpdateMonitorResponse
from protos.event.base_pb2 import EventKey
from protos.event.monitor_pb2 import UpdateMonitorOp


def get_db_monitor_dict(db_name=None, requested_name=None, primary_key=None, secondary_key=None, is_active=None,
                        is_generated=False):
    db_monitor_default = {'name': db_name}
    if requested_name:
        db_monitor_default['name'] = requested_name
    if primary_key:
        db_monitor_default['primary_key_id'] = primary_key['id']
    if secondary_key:
        db_monitor_default['secondary_key_id'] = secondary_key['id']
    if is_active is not None:
        db_monitor_default['is_active'] = is_active
    if is_generated:
        db_monitor_default['is_generated'] = is_generated
    return db_monitor_default


def get_db_monitor(account: Account, monitor_id=None, monitor_name=None, is_active=None, primary_key_id=None,
                   secondary_key_id=None):
    filters = {}
    if monitor_id:
        filters['id'] = monitor_id
    if is_active is not None:
        filters['is_active'] = is_active
    if monitor_name:
        filters['name'] = monitor_name
    if primary_key_id:
        filters['primary_key_id'] = primary_key_id
    if secondary_key_id:
        filters['secondary_key_id'] = secondary_key_id
    try:
        return account.monitor_set.filter(**filters)
    except Exception:
        return None


def create_monitors(account: Account, monitor_name: str, primary_event_key_id, secondary_event_key_id,
                    is_generated=False) -> (Monitor, bool, str):
    if not monitor_name or not primary_event_key_id or not secondary_event_key_id:
        return None, False, "Invalid Request: Missing monitor name/primary/secondary keys"

    keys = account.eventkey_set.filter(id__in=[primary_event_key_id, secondary_event_key_id]).values_list('id',
                                                                                                          flat=True)
    if not keys or len(keys) != 2:
        return None, False, "Invalid Request: Check Primary and Secondary Event keys"

    db_monitors = get_db_monitor(account, primary_key_id=primary_event_key_id, secondary_key_id=secondary_event_key_id)
    if not db_monitors.exists():
        try:
            db_monitor = Monitor(account=account,
                                 name=monitor_name,
                                 primary_key_id=primary_event_key_id,
                                 secondary_key_id=secondary_event_key_id,
                                 is_active=True,
                                 is_generated=is_generated)
            db_monitor.save()
            return db_monitor, True, None
        except IntegrityError:
            return None, False, f"Integrity Error: Monitor with {monitor_name} already exists"
    else:
        # Uniqueness constraint is on account and monitor name
        db_named_monitors = get_db_monitor(account, monitor_name=monitor_name)
        if db_named_monitors.exists():
            db_named_monitor = db_named_monitors.first()
            if db_named_monitor.primary_key_id != primary_event_key_id or db_named_monitor.secondary_key_id != secondary_event_key_id:
                return None, False, f"Duplicate Name: Monitor {monitor_name} with different keys already exists"
            if db_named_monitor.is_active:
                return db_named_monitor, False, f"Active Monitor Found: {monitor_name} : " \
                                                f"{primary_event_key_id} : {secondary_event_key_id} already exists"
            else:
                db_monitor = db_named_monitor
        else:
            active_db_monitor = db_monitors.filter(is_active=True)
            if active_db_monitor.exists():
                active_db_monitor = active_db_monitor.first()
                return active_db_monitor, False, f"Active Monitor Found: {active_db_monitor.name} " \
                                                 f"with {primary_event_key_id} and " \
                                                 f"{secondary_event_key_id} already exists"
            db_monitor = db_monitors.first()

        update_ops = [UpdateMonitorOp(op=UpdateMonitorOp.Op.UPDATE_MONITOR_STATUS,
                                      update_monitor_status=UpdateMonitorOp.UpdateMonitorStatus(
                                          is_active=BoolValue(value=True))),
                      UpdateMonitorOp(op=UpdateMonitorOp.Op.UPDATE_MONITOR_IS_GENERATED,
                                      update_monitor_is_generated=UpdateMonitorOp.UpdateMonitorIsGenerated(
                                          is_generated=BoolValue(value=is_generated))),
                      UpdateMonitorOp(op=UpdateMonitorOp.Op.UPDATE_MONITOR_NAME,
                                      update_monitor_name=UpdateMonitorOp.UpdateMonitorName(
                                          name=StringValue(value=monitor_name)))]
        monitor_update_processor.update(db_monitor, update_ops)
        return db_monitor, False, None


def update_monitors(account: Account, request: CreateOrUpdateMonitorRequest):
    monitor_id = request.id
    if not monitor_id:
        return CreateOrUpdateMonitorResponse(success=BoolValue(value=False),
                                             message=Message(title='Error updating monitor',
                                                             description='Missing monitor id'))
    db_monitor = get_db_monitor(account, monitor_id=monitor_id)
    db_monitor = db_monitor.first()
    if not db_monitor:
        return CreateOrUpdateMonitorResponse(success=BoolValue(value=False),
                                             message=Message(title='Error updating monitor',
                                                             description=f'Monitor with id {monitor_id} not found'))
    update_ops: [UpdateMonitorOp] = []
    if request.name:
        update_ops.append(UpdateMonitorOp(op=UpdateMonitorOp.Op.UPDATE_MONITOR_NAME,
                                          update_monitor_name=UpdateMonitorOp.UpdateMonitorName(
                                              name=StringValue(value=request.name))))
    if request.primary_event_key_id:
        update_ops.append(UpdateMonitorOp(op=UpdateMonitorOp.Op.UPDATE_MONITOR_PRIMARY_KEY,
                                          update_monitor_primary_key=UpdateMonitorOp.UpdateMonitorPrimaryKey(
                                              primary_event_key=EventKey(id=request.primary_event_key_id))))
    if request.secondary_event_key_id:
        update_ops.append(UpdateMonitorOp(op=UpdateMonitorOp.Op.UPDATE_MONITOR_SECONDARY_KEY,
                                          update_monitor_secondary_key=UpdateMonitorOp.UpdateMonitorSecondaryKey(
                                              secondary_event_key=EventKey(id=request.secondary_event_key_id))))
    if request.is_active is not None:
        if not request.is_active.value:
            if not account.entitymonitormapping_set.filter(monitor_id=db_monitor.id).exists():
                update_ops.append(UpdateMonitorOp(op=UpdateMonitorOp.Op.UPDATE_MONITOR_STATUS,
                                                  update_monitor_status=UpdateMonitorOp.UpdateMonitorStatus(
                                                      is_active=BoolValue(value=request.is_active.value))))
            else:
                update_ops.append(UpdateMonitorOp(op=UpdateMonitorOp.Op.UPDATE_MONITOR_STATUS,
                                                  update_monitor_is_generated=UpdateMonitorOp.UpdateMonitorStatus(
                                                      is_active=BoolValue(value=True))))
                update_ops.append(UpdateMonitorOp(op=UpdateMonitorOp.Op.UPDATE_MONITOR_IS_GENERATED,
                                                  update_monitor_is_generated=UpdateMonitorOp.UpdateMonitorIsGenerated(
                                                      is_generated=BoolValue(value=True))))
        else:
            update_ops.append(UpdateMonitorOp(op=UpdateMonitorOp.Op.UPDATE_MONITOR_STATUS,
                                              update_monitor_status=UpdateMonitorOp.UpdateMonitorStatus(
                                                  is_active=BoolValue(value=request.is_active.value))))
            if db_monitor.is_generated:
                update_ops.append(UpdateMonitorOp(op=UpdateMonitorOp.Op.UPDATE_MONITOR_IS_GENERATED,
                                                  update_monitor_is_generated=UpdateMonitorOp.UpdateMonitorIsGenerated(
                                                      is_generated=BoolValue(value=False))))

    monitor_update_processor.update(db_monitor, update_ops)
    return CreateOrUpdateMonitorResponse(success=BoolValue(value=True), message=Message(title='Monitor updated'))
