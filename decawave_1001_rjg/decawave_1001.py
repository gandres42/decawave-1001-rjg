import time
from bitstring import BitArray
import serial
from enum import Enum

from .messages.dwm_interrupt_config_request import DwmInterruptConfigRequest
from .messages.dwm_config_response import DwmConfigResponse
from .messages.dwm_location_response import DwmLocationResponse
from .messages.dwm_position_response import DwmPositionResponse
from .messages.dwm_request import DwmRequests
from .messages.dwm_response import DwmResponse
from .messages.dwm_status_response import DwmStatusResponse
from .messages.dwm_version_response import DwmVersionResponse
from .messages.tlv_message import TlvMessage

class Decawave1001Driver:
    def __init__(self, serial_port: str):
        self.max_retry_count = 5    # Number of times to retry a failed message
        self.timestamp = time.time()
        self.uart = serial.Serial(serial_port, 115200, timeout=0.005)

    def _init_decawave(self):
        self.soft_reset()
        self._enable_data_ready_pin()

    def _enable_data_ready_pin(self):
        request = DwmInterruptConfigRequest(True, False)
        self._send_and_get_response(request)

    def close(self):
        """Closes the UART connection. This should be called on shutdown."""
        self.uart.close()

    def soft_reset(self):
        """Returns the DWM tag's state machine to Idle so it'll be ready for a new request.
        Use this to reset the tag when the message responses are out of sync."""
        # Simply send 0xFF 3 times in a row.
        self.uart.write(bytearray([0xFF, 0xFF, 0xFF]))

    def reset(self):
        """Reboots the Decawave module. This takes a couple of seconds."""
        self.uart.write(DwmRequests.dwm_reset.message)
        # It takes a good while for the reset to complete
        time.sleep(2.5)
        self._init_decawave()

    def get_cfg(self) -> DwmConfigResponse:
        response = self._send_and_get_response(DwmRequests.dwm_cfg_get)
        return DwmConfigResponse(response)

    def get_ver(self) -> DwmVersionResponse:
        response = self._send_and_get_response(DwmRequests.dwm_ver_get)
        return DwmVersionResponse(response)

    def get_status(self) -> DwmStatusResponse:
        response = self._send_and_get_response(DwmRequests.dwm_status_get)
        return DwmStatusResponse(response)

    def get_pos(self) -> DwmPositionResponse:
        response = self._send_and_get_response(DwmRequests.dwm_pos_get)
        return DwmPositionResponse(response)

    def get_loc(self) -> DwmLocationResponse:
        response = self._send_and_get_response(DwmRequests.dwm_loc_get)
        return DwmLocationResponse(response)

    def _send_and_get_response(self, request: TlvMessage) -> bytes:
        # send request
        self.uart.write(request.message)

        # get response
        t1 = self.uart.read(1)
        l1 = self.uart.read(1)
        v1 = self.uart.read(int.from_bytes(l1, byteorder='little'))
        if int.from_bytes(v1, byteorder="little") == 0:
            t2 = self.uart.read(1)
            l2 = self.uart.read(1)
            v2 = b''
            tmp_byte = 0XFF
            while tmp_byte != b'':
                tmp_byte = self.uart.read(1)
                v2 = v2 + tmp_byte
            return t1 + l1 + v1 + t2 + l2 + v2
        responseValueCodes = ['OK', 'UNKNOWN COMMAND', 'INTERNAL ERROR', 'INVALID PARAMETER', 'TAG BUSY', 'OPERATION NOT PERMITTED']
        raise RuntimeError("Response error: " + responseValueCodes[int.from_bytes(v1, byteorder="little")])