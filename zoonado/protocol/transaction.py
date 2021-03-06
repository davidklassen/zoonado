from __future__ import unicode_literals

import logging
import struct

from six import BytesIO

from zoonado import exc

from .request import Request
from .response import Response, response_xref
from .part import Part
from .primitives import Int, Bool


error_struct = struct.Struct("!" + Int.fmt)


log = logging.getLogger(__name__)


class MultiHeader(Part):
    """
    """
    parts = (
        ("type", Int),
        ("done", Bool),
        ("error", Int),
    )


class TransactionRequest(Request):
    """
    """
    opcode = 14

    def __init__(self, *args, **kwargs):
        super(TransactionRequest, self).__init__(*args, **kwargs)
        self.requests = []

    def add(self, request):
        self.requests.append(request)

    def serialize(self, xid=None):
        buff = BytesIO()

        formats = []
        data = []
        if xid is not None:
            formats.append(Int.fmt)
            data.append(xid)
        if self.opcode:
            formats.append(Int.fmt)
            data.append(self.opcode)

        for request in self.requests:
            header = MultiHeader(type=request.opcode, done=False, error=-1)
            header_format, header_data = header.render()
            formats.append(header_format)
            data.extend(header_data)

            payload_format, payload_data = request.render()
            formats.append(payload_format)
            data.extend(payload_data)

        footer = MultiHeader(type=-1, done=True, error=-1)
        footer_format, footer_data = footer.render()
        formats.append(footer_format)
        data.extend(footer_data)

        buff.write(struct.pack("!" + "".join(formats), *data))

        return buff.getvalue()

    def __str__(self):
        return "Txn[%s]" % ", ".join(map(str, self.requests))


class TransactionResponse(Response):
    """
    """
    opcode = 14

    def __init__(self, *args, **kwargs):
        super(TransactionResponse, self).__init__(*args, **kwargs)
        self.responses = []

    @classmethod
    def deserialize(cls, raw_bytes):
        instance = cls()

        header, offset = MultiHeader.parse(raw_bytes, 0)
        while not header.done:
            if header.type == -1:
                error_code = error_struct.unpack_from(raw_bytes, offset)[0]
                offset += error_struct.size
                instance.responses.append(exc.get_response_error(error_code))
                header, offset = MultiHeader.parse(raw_bytes, offset)
                continue

            response_class = response_xref[header.type]

            response, offset = response_class.parse(raw_bytes, offset)
            instance.responses.append(response)

            header, offset = MultiHeader.parse(raw_bytes, offset)

        return instance

    def __str__(self):
        return "Txn[%s]" % ", ".join(map(str, self.responses))
