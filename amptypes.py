"""
Copyright (c) 2006-2007

Henrik Thostrup Jensen <thostrup@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import struct

from twisted.protocols import amp



class TypedDictionary(amp.Argument):
    """
    Represents a dictionary. The key and value types of the dictionary
    must be specified, but otherwise the dictionary is free form.
    """
    PACKFORMAT = '!H'

    def __init__(self, keyType, valueType):
        self.keyType = keyType
        self.valueType = valueType


    def fromStringProto(self, inString, proto):
        d = {}
        tail = inString
        while tail:
            lks = tail[:2]
            lk = struct.unpack(self.PACKFORMAT, lks)[0]
            ks = tail[2:lk+2]
            k = self.keyType.fromString(ks)
            tail = tail[lk+2:]

            lvs = tail[:2]
            lv = struct.unpack(self.PACKFORMAT, lvs)[0]
            vs = tail[2:lv+2]
            v = self.valueType.fromString(vs)
            tail = tail[lv+2:]

            d[k] = v

        return d


    def toStringProto(self, inObject, proto):
        l = []
        for k,v in inObject.items():
            ks = self.keyType.toString(k)
            l.append(struct.pack(self.PACKFORMAT, len(ks)))
            l.append(ks)
            vs = self.valueType.toString(v)
            l.append(struct.pack(self.PACKFORMAT, len(vs)))
            l.append(vs)
        return ''.join(l)



class TypedList(amp.Argument):
    """
    Represents a list. The elect type of the list must be specified.
    The list can have any number of elements (while respeciting some
    fundemental limits of the AMP protocol.
    """
    PACKFORMAT = '!H'

    def __init__(self, elementType):
        self.elementType = elementType


    def fromStringProto(self, inString, proto):
        l = []
        tail = inString
        while tail:
            les = tail[:2]
            le = struct.unpack(self.PACKFORMAT, les)[0]
            e = tail[2:le+2]
            l.append(self.elementType.fromString(e))
            tail = tail[le+2:]
        return l


    def toStringProto(self, inObject, proto):
        l = []
        for e in inObject:
            es = self.elementType.toString(e)
            l.append(struct.pack(self.PACKFORMAT, len(es)))
            l.append(es)
        return ''.join(l)
