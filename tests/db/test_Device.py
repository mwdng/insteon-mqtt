#===========================================================================
#
# Tests for: insteont_mqtt/db/Device.py
#
#===========================================================================
import insteon_mqtt as IM
import insteon_mqtt.message as Msg


class Test_Device:
    #-----------------------------------------------------------------------
    def test_basic(self):
        obj = IM.db.Device()
        assert len(obj) == 0

        assert obj.is_current(0) is False
        obj.delta = 1
        assert obj.is_current(1) is True
        obj.clear_delta()
        assert obj.is_current(1) is False

        addr = IM.Address(0x10, 0xab, 0x1c)
        flags = Msg.Flags(Msg.Flags.Type.DIRECT, True)
        db_flags = Msg.DbFlags(in_use=True, is_controller=True,
                               last_record=False)
        data = bytes([0x01, 0x02, 0x03])
        raw = [0x00, 0x01,
               0xfe, 0x10,  # mem_loc
               0x00, db_flags.to_bytes()[0],
               0x03,  # group
               addr.ids[0], addr.ids[1], addr.ids[2],
               data[0], data[1], data[2], 0x06]
        msg = Msg.InpExtended(addr, addr, flags, 0x00, 0x00, bytes(raw))
        obj.handle_db_rec(msg)

        # add same addr w/ different group
        raw[6] = 0x02
        msg.data = raw
        obj.handle_db_rec(msg)

        # new addr, same group
        addr2 = IM.Address(0x10, 0xab, 0x1d)
        raw[9] = 0x1d
        msg.data = raw
        obj.handle_db_rec(msg)

        # responder - not in a group
        db_flags = Msg.DbFlags(in_use=True, is_controller=False,
                               last_record=False)
        raw[5] = db_flags.to_bytes()[0]
        msg.data = raw
        obj.handle_db_rec(msg)

        # in use = False
        db_flags = Msg.DbFlags(in_use=False, is_controller=True,
                               last_record=False)
        raw[5] = db_flags.to_bytes()[0]
        msg.data = raw
        obj.handle_db_rec(msg)

        assert len(obj.entries) == 4
        assert len(obj.unused) == 1
        assert len(obj.groups) == 2

        grp = obj.find_group(0x02)
        assert len(grp) == 2
        assert grp[0].addr == addr
        assert grp[1].addr == addr2

        e = obj.find(addr, 0x02, 'CTRL')
        assert e.addr == addr
        assert e.group == 0x02
        assert e.db_flags.is_controller is True

        e = obj.find(addr2, 0x02, 'RESP')
        assert e.addr == addr2
        assert e.group == 0x02
        assert e.db_flags.is_responder is True

        e = obj.find(addr, 0x05, 'RESP')
        assert e is None

        str(obj)

        j = obj.to_json()
        obj2 = IM.db.Device.from_json(j)
        assert len(obj2.entries) == 4
        assert len(obj2.unused) == 1
        assert len(obj2.groups) == 2

        obj2.clear()
        assert len(obj2) == 0
        assert len(obj2.entries) == 0
        assert len(obj2.unused) == 0
        assert len(obj2.groups) == 0
