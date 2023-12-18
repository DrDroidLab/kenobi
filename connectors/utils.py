from datetime import datetime


def find_datetime_format_and_convert(timestamp_value):
    potential_formats = [
        '%Y-%m-%d %H:%M:%S',  # '2023-09-04 12:34:56'
        '%Y-%m-%d %I:%M:%S %p',  # '2023-09-04 12:34:56 AM/PM'
        '%Y-%m-%d %H:%M:%S.%f',  # '2023-09-04 12:34:56.123456'
        '%Y-%m-%d %H:%M',  # '2023-09-04 12:34'
        '%Y-%m-%d',  # '2023-09-04'
        '%d-%m-%Y %H:%M:%S',  # '04-09-2023 12:34:56'
        '%d-%m-%Y %I:%M:%S %p',  # '04-09-2023 12:34:56 AM/PM'
        '%d-%m-%Y %H:%M:%S.%f',  # '04-09-2023 12:34:56.123456'
        '%d-%m-%Y %H:%M',  # '04-09-2023 12:34'
        '%d-%m-%Y',  # '04-09-2023'
        '%m/%d/%Y %H:%M:%S',  # '09/04/2023 12:34:56'
        '%m/%d/%Y %I:%M:%S %p',  # '09/04/2023 12:34:56 AM/PM'
        '%m/%d/%Y %H:%M:%S.%f',  # '09/04/2023 12:34:56.123456'
        '%m/%d/%Y %H:%M',  # '09/04/2023 12:34'
        '%m/%d/%Y',  # '09/04/2023'
        '%Y-%m-%d %H:%M:%S UTC',
        '%Y-%m-%dT%H:%M:%S.%fZ',
    ]

    timestamp_str = str(timestamp_value)
    try:
        timestamp_float = float(timestamp_str)
        epoch_value = timestamp_str.split('.')[0]
        if len(epoch_value) == 10:
            return int(timestamp_float * 1000)
        elif len(epoch_value) == 13:
            return int(timestamp_float)
        else:
            return None
    except ValueError:
        pass
    try:
        timestamp_int = int(timestamp_str)
        if len(timestamp_str) == 10:
            return timestamp_int * 1000
        elif len(timestamp_str) == 13:
            return timestamp_int
        else:
            return None
    except ValueError:
        pass
    for format_str in potential_formats:
        try:
            parsed_datetime = datetime.strptime(timestamp_str, format_str)
            return int(parsed_datetime.timestamp() * 1000)
        except ValueError:
            pass
    return None