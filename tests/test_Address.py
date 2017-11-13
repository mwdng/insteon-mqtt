import sys
sys.path.insert(0,"..")
import insteon_mqtt as IM
from pytest import assume

class Test_Address:
    def check(self, addr, id):
        ids = [(id & 0xff0000) >> 16, (id & 0xff00) >> 8, (id & 0xff)]
        hex = "%02X.%02X.%02X" % tuple(ids)
        assert(addr.id == id)
        assert(addr.ids == ids)
        assert(addr.bytes == bytes(ids))
        assert(addr.hex == hex)

    def test_id(self):
        a = IM.Address(123456)
        self.check(a, 123456)
        
    def test_addr(self):
        a = IM.Address(123456)
        b = IM.Address(a)
        self.check(b, a.id)

    def test_str1(self):
        a = IM.Address('01e240')
        self.check(a, 123456)

    def test_str2(self):
        a = IM.Address('01E240')
        self.check(a, 123456)
        
    def test_str3(self):
        a = IM.Address('01.E2.40')
        self.check(a, 123456)
        
    def test_str4(self):
        a = IM.Address('01 E2 40')
        self.check(a, 123456)
        
    def test_str5(self):
        a = IM.Address('01:e2:40')
        self.check(a, 123456)
        
    def test_id3(self):
        a = IM.Address(0x01, 0xe2, 0x40)
        self.check(a, 123456)
        
