from __future__ import unicode_literals

from .request import Request
from .response import Response
from .stat import Stat
from .acl import ACL
from .primitives import UString, Int, Buffer, Vector


class CreateRequest(Request):
    """
    """
    opcode = 1

    writes_data = True

    EPHEMERAL_FLAG = 1 << 0
    SEQUENTIAL_FLAG = 1 << 1
    CONTAINER_FLAG = 1 << 2

    parts = (
        ("path", UString),
        ("data", Buffer),
        ("acl", Vector.of(ACL)),
        ("flags", Int),
    )

    def set_flags(self, ephemeral=False, sequential=False, container=False):
        flags = 0
        if ephemeral:
            flags |= self.EPHEMERAL_FLAG
        if sequential:
            flags |= self.SEQUENTIAL_FLAG
        if container:
            flags |= self.CONTAINER_FLAG

        self.flags = flags


class CreateResponse(Response):
    """
    """
    opcode = 1

    parts = (
        ("path", UString),
    )


class Create2Request(CreateRequest):
    """
    """
    opcode = 15


class Create2Response(Response):
    """
    """
    opcode = 15

    parts = (
        ("path", UString),
        ("stat", Stat),
    )
