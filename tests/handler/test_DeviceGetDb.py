#===========================================================================
#
# Tests for: insteont_mqtt/handler/DeviceGetDb.py
#
#===========================================================================
import insteon_mqtt as IM
import insteon_mqtt.message as Msg


class Test_DeviceGetDb:
    def test_acks(self):
        proto = None
        calls = []

        addr = IM.Address('0a.12.34')
        handler = IM.handler.DeviceGetDb(addr, calls.append)

        # Normal nak
        std_ack = Msg.OutStandard.direct(addr, 0x2f, 0x00)
        std_ack.is_ack = False
        r = handler.msg_received(proto, std_ack)
        assert r == Msg.CONTINUE

        # Wrong address
        nomatch = Msg.OutStandard.direct(IM.Address('0a.12.35'), 0x2f, 0x00)
        std_ack.is_ack = True
        r = handler.msg_received(proto, nomatch)
        assert r == Msg.UNKNOWN

        # Wrong command
        std_ack.cmd1 = 0x11
        r = handler.msg_received(proto, std_ack)
        assert r == Msg.UNKNOWN

        # Try w/ an extended msg.
        ext_data = bytes(14)
        ext_ack = Msg.OutExtended.direct(addr, 0x2f, 0x00, ext_data)
        ext_ack.is_ack = True
        r = handler.msg_received(proto, ext_ack)
        assert r == Msg.CONTINUE

        r = handler.msg_received(proto, "dummy")
        assert r == Msg.UNKNOWN

        assert calls == []

    #-----------------------------------------------------------------------
    def test_recs(self):
        proto = None
        calls = []

        addr = IM.Address('0a.12.34')
        handler = IM.handler.DeviceGetDb(addr, calls.append)

        flags = Msg.Flags(Msg.Flags.Type.DIRECT, True)
        data = bytes([0x01, 0, 0, 0, 0, 0, 0, 0x01, 0, 0, 0, 0, 0, 0])
        msg = Msg.InpExtended(addr, addr, flags, 0x2f, 0x00, data)

        r = handler.msg_received(proto, msg)
        assert r == Msg.CONTINUE
        assert len(calls) == 1
        assert calls[0] == msg

        msg.data = bytes(14)
        r = handler.msg_received(proto, msg)
        assert r == Msg.FINISHED
        assert len(calls) == 2
        assert calls[1] is None

        # no match
        msg.cmd1 = 0x00
        r = handler.msg_received(proto, msg)
        assert r == Msg.UNKNOWN


#===========================================================================
