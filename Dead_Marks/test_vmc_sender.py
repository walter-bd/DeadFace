import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))

from vmc_sender import (
    VMC_BLENDSHAPE_NAME_MAP,
    VmcBlendshapeSender,
    clamp_blendshape_value,
    map_blendshape_name,
)


class FakeClient:
    def __init__(self):
        self.messages = []

    def send_message(self, address, payload):
        self.messages.append((address, payload))


class VmcSenderTests(unittest.TestCase):
    def test_clamp_blendshape_value_limits_to_zero_and_one(self):
        self.assertEqual(clamp_blendshape_value(-0.5), 0.0)
        self.assertEqual(clamp_blendshape_value(0.25), 0.25)
        self.assertEqual(clamp_blendshape_value(1.5), 1.0)

    def test_map_blendshape_name_uses_configured_mapping(self):
        source_name = "browInnerUp"
        expected_name = VMC_BLENDSHAPE_NAME_MAP[source_name]
        self.assertEqual(map_blendshape_name(source_name), expected_name)
        self.assertEqual(map_blendshape_name("jawOpen"), "jawOpen")

    def test_send_blendshapes_emits_val_messages_then_apply(self):
        client = FakeClient()
        sender = VmcBlendshapeSender(client=client)

        sender.send_blendshapes(
            {
                "mouthClose": 1.25,
                "jawOpen": -0.25,
            },
            ["mouthClose", "jawOpen"],
        )

        self.assertEqual(
            client.messages,
            [
                ("/VMC/Ext/Blend/Val", ["mouthClose", 1.0]),
                ("/VMC/Ext/Blend/Val", ["jawOpen", 0.0]),
                ("/VMC/Ext/Blend/Apply", []),
            ],
        )

    def test_send_blendshapes_without_client_is_noop(self):
        with patch.object(VmcBlendshapeSender, "_create_client", return_value=None):
            sender = VmcBlendshapeSender(client=None)
        self.assertFalse(sender.send_blendshapes({"jawOpen": 0.3}, ["jawOpen"]))


if __name__ == "__main__":
    unittest.main()
