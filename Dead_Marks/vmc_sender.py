from __future__ import annotations

from typing import Iterable


VMC_BLENDSHAPE_NAME_MAP = {
    "browInnerUp": "browInnerUp",
}


def clamp_blendshape_value(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def map_blendshape_name(name: str) -> str:
    return VMC_BLENDSHAPE_NAME_MAP.get(name, name)


class VmcBlendshapeSender:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 39540,
        client=None,
        debug: bool = False,
        debug_message_limit: int = 5,
    ):
        self.host = host
        self.port = int(port)
        self.client = client
        self.debug = debug
        self.debug_message_limit = debug_message_limit
        self._debug_messages_printed = 0
        self._send_failed = False

        if self.client is None:
            self.client = self._create_client()

    def _create_client(self):
        try:
            from pythonosc.udp_client import SimpleUDPClient
        except ImportError:
            print(
                "[WARN] VMC output requested but python-osc is not installed. "
                "Install dependency with: pip install python-osc"
            )
            return None

        try:
            return SimpleUDPClient(self.host, self.port)
        except Exception as exc:
            print(f"[WARN] Could not create VMC OSC client for {self.host}:{self.port}: {exc}")
            return None

    def send_blendshapes(self, blendshape_values: dict[str, float], blendshape_order: Iterable[str]):
        if self.client is None:
            return False

        try:
            for name in blendshape_order:
                mapped_name = map_blendshape_name(name)
                value = clamp_blendshape_value(blendshape_values.get(name, 0.0))
                payload = [mapped_name, value]
                self.client.send_message("/VMC/Ext/Blend/Val", payload)
                self._debug_log("/VMC/Ext/Blend/Val", payload)

            self.client.send_message("/VMC/Ext/Blend/Apply", [])
            self._debug_log("/VMC/Ext/Blend/Apply", [])
            self._send_failed = False
            return True
        except Exception as exc:
            if not self._send_failed:
                print(f"[WARN] VMC output send failed: {exc}")
                self._send_failed = True
            return False

    def _debug_log(self, address: str, payload):
        if not self.debug:
            return
        if self._debug_messages_printed >= self.debug_message_limit:
            return
        print(f"[VMC] {address} {payload}")
        self._debug_messages_printed += 1
