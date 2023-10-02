import json
from unittest import TestCase

from protos.test.test_pb2 import TestMessage
from utils.proto_utils import proto_to_json, json_to_proto


class TestProtoUtils(TestCase):
    def test_proto_to_json(self):
        tm = TestMessage(
            workflow_name='workflow_name',
            workflow_id=1000,
            test_nested_message=TestMessage.TestNestedMessage(
                string_field='string', bool_field=True
            )
        )

        snake_case = """
        {
          "workflow_name": "workflow_name",
          "workflow_id": "1000",
          "test_nested_message": {
            "string_field": "string",
            "bool_field": true
          }
        }
        """
        self.assertEqual(proto_to_json(tm), json.dumps(json.loads(snake_case), indent=2))

        camel_case = """
        {
          "workflowName": "workflow_name",
          "workflowId": "1000",
          "testNestedMessage": {
            "stringField": "string",
            "boolField": true
          }
        }
        """
        self.assertEqual(proto_to_json(tm, use_snake_case=False), json.dumps(json.loads(camel_case), indent=2))

    def test_json_to_proto(self):
        expected_out = tm = TestMessage(
            workflow_name='workflow_name',
            workflow_id=1000,
            test_nested_message=TestMessage.TestNestedMessage(
                string_field='string', bool_field=True
            )
        )

        snake_case = """
        {
          "workflow_name": "workflow_name",
          "workflow_id": "1000",
          "test_nested_message": {
            "string_field": "string",
            "bool_field": true
          }
        }
        """

        self.assertEqual(json_to_proto(snake_case, TestMessage), expected_out)

        camel_case = """
        {
          "workflowName": "workflow_name",
          "workflowId": "1000",
          "testNestedMessage": {
            "stringField": "string",
            "boolField": true
          }
        }
        """
        self.assertEqual(json_to_proto(camel_case, TestMessage), expected_out)

