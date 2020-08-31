import re

class NdnTlvPrinter(object):

    """
    Formatted printing of a NDN TLV to stdout.


    Implemented Specifications:

       - NDN Packet Format Specification 0.2-2 documentation
         http://named-data.net/doc/NDN-TLV/current/intro.html (January 2018)

       - NDNLPv2 (link protocol)
         https://redmine.named-data.net/projects/nfd/wiki/NDNLPv2 (February 2018)


    Example:
        0000 |  06 20 -- <type='Interest Packet', length=32>
        0002 |     07 13 -- <type='Name', length=19>
        0004 |        08 04 -- <type='GenericNameComponent', length=4>
        0006 |           74 68 69 73                                               this
        0010 |        08 02 -- <type='GenericNameComponent', length=2>
        0012 |           69 73                                                     is
        0014 |        08 01 -- <type='GenericNameComponent', length=1>
        0016 |           61                                                        a
        0017 |        08 04 -- <type='GenericNameComponent', length=4>
        0019 |           6E 61 6D 65                                               name
        0023 |     14 00 -- <type='MetaInfo', length=0>
        0025 |     15 07 -- <type='Content', length=7>
        0027 |        70 61 79 6C 6F 61 64                                         payload

    """
    #removed 23 signature value and 22 SignatureInfo, 21 Content (for picn-key-gen)
    __has_blob_value = {21, 2, 8, 1, 10, 13, 14, 17, 12, 24, 25, 27, 28, 29, 35, 36 ,38, 39, 801}

    __known_type_names = {
                           2: "ContentType_Key",
                           5: "Interest Packet",
                           6: "Content Object Packet",
                           7: "Name",
                           8: "GenericNameComponent",
                           1: "ImplicitSha256DigestComponent",
                           9: "Selectors",
                          10: "Nonce",
                          12: "InterestLifetime",
                          30: "ForwardingHint / Preference",
                          13: "MinSuffixComponents",
                          14: "MaxSuffixComponents",
                          15: "PublisherPublicKeyLocator",
                          16: "Exclude",
                          17: "ChildSelector",
                          18: "MustBeFresh",
                          19: "Any",
                          20: "MetaInfo",
                          21: "Content",
                          22: "SignatureInfo",
                          23: "SignatureValue",
                          24: "ContentType",
                          25: "FreshnessPeriod",
                          26: "FinalBlockId",
                          27: "SignatureType",
                          28: "KeyLocator",
                          29: "KeyDigest",
                          31: "Delegation",
                          34: "Signature",
                          35: "IdentityProof",
                          36:"OutputSignature",
                          37:"InputProviniance",
                          38:"SignatureSignature",
                          39:"ArgumentIdentifier",
                          80: "Fragment (link protocol)",           # NDN Link Protocol v2
                          81: "Sequence (link protocol)",           # NDN Link Protocol v2
                          82: "FragIndex (link protocol)",          # NDN Link Protocol v2
                          83: "FragCount (link protocol)",          # NDN Link Protocol v2
                          84: "HopCount (link protocol)",           # NDN Link Protocol v2
                          98: "PitToken (link protocol)",           # NDN Link Protocol v2
                         100: "LpPacket (link protocol)",           # NDN Link Protocol v2
                         800: "Nack (link protocol)",               # NDN Link Protocol v2
                         801: "NackReason (link protocol)",         # NDN Link Protocol v2
                         816: "NextHopFaceId (link protocol)",      # NDN Link Protocol v2
                         817: "IncomingFaceId (link protocol)",     # NDN Link Protocol v2
                         820: "CachePolicy (link protocol)",        # NDN Link Protocol v2
                         821: "CachePolicyType (link protocol)",    # NDN Link Protocol v2
                         832: "CongestionMark (link protocol)",     # NDN Link Protocol v2
                         836: "Ack (link protocol)",                # NDN Link Protocol v2
                         840: "TxSequence (link protocol)",         # NDN Link Protocol v2
                         844: "NonDiscovery (link protocol)",       # NDN Link Protocol v2
                         848: "PrefixAnnouncement (link protocol)"  # NDN Link Protocol v2
                         }

    __nack_reason_names = {
                            0: "None (reserved)",
                           50: "Congestion",
                          100: "Duplicate",
                          150: "NoRoute"
                          }


    def __init__(self, wire_format:bytearray) -> None:
        """
        Formatted printing of a NDN TLV packet in wire format.
        :param wire_format: NDN TLV in wire format
        """
        self.__wire_format = wire_format


    def formatted_print(self) -> None:
        self.__position = 0
        self.__indention_level = 0
        print()
        self.__print_tlv()
        print()



    def __get_type_name(self, n):
        try:
            return self.__known_type_names[n]
        except:
            return "UNKNOWN"


    def byte_to_hex(n) -> str:
        """
        Convert a byte to string (hexadecimal representation)
        Example: 255 to FF
        :param n:    Byte (integer between 0 and 255)
        :return:     Hexadecimal representation
        """
        as_hex = hex(n)[2:]
        if len(as_hex) == 1:
            return "0" + as_hex.upper()
        else:
            return as_hex.upper()


    def print_without_newline(exp:str) -> None:
        """
        Print an expression without newline
        :param exp:   Expression to print
        :return:      None
        """
        print(exp, end="")


    def __print_indention(self) -> None:
        """
        Print indention
        :return: None
        """
        NdnTlvPrinter.print_without_newline(str(self.__position).zfill(4) + " | " + 3 * self.__indention_level * " ")


    def __print_tlv(self):
        print()
        self.__print_indention()
        type_value = self.__print_num()
        length = self.__print_num()
        type_value_description = self.__get_type_name(type_value)
        NdnTlvPrinter.print_without_newline(" -- <type='{}', length={}>".format(type_value_description, length))

        self.__indention_level += 1
        if type_value_description == "UNKNOWN":
            NdnTlvPrinter.__print_blob(self, length)
        else:
            if type_value in self.__has_blob_value:
                self.__print_blob(length)
            else:
                next_tlv_start = self.__position + length
                while(self.__position < next_tlv_start):
                    self.__print_tlv()

            self.__indention_level -= 1


    def __print_num(self) -> int:
        NdnTlvPrinter.print_without_newline(" ")
        current_hex = self.__wire_format[self.__position]
        NdnTlvPrinter.print_without_newline(NdnTlvPrinter.byte_to_hex(current_hex))
        if current_hex < 253:
            value = current_hex
            offset = 1
        else:
            if current_hex == 253: offset =  3
            if current_hex == 254: offset =  5
            if current_hex == 255: offset =  9
            value = 0
            for i in range(1, offset):
                next_octet = self.__wire_format[self.__position + i]
                NdnTlvPrinter.print_without_newline(" ")
                NdnTlvPrinter.print_without_newline(NdnTlvPrinter.byte_to_hex(next_octet))
                value += next_octet << (offset-1-i) * 8
        self.__position += offset
        return value


    def __bytes_to_printable_char(self, b: bytes) -> str:
        """
        Convert bytes to a printable string
        :param b: bytes
        :return: printable string
        """
        chars_to_print = """!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüý"""


        try:
            as_str = b.decode('unicode_escape')
        except:
            print("ERROR: PRINT")
            as_str=" "

        return ''.join(map(lambda c: c if c in chars_to_print else '�', as_str))


    def __print_blob(self, len) -> None:
        """
        Print a Blob
        :param len: length of blob
        :return: None
        """
        idx = 0
        for e in self.__wire_format[self.__position:self.__position+len]:
            if idx % 8 == 0:
                print()
                self.__print_indention()
                NdnTlvPrinter.print_without_newline(" ")
            else:
                NdnTlvPrinter.print_without_newline(" ")
            self.__position += 1
            idx += 1
            NdnTlvPrinter.print_without_newline(NdnTlvPrinter.byte_to_hex(e))

            #if (idx % 8 == 0 & idx != len):
            if idx % 8 == 0 :
                NdnTlvPrinter.print_without_newline("\t".expandtabs(50 - 3 * self.__indention_level))
                NdnTlvPrinter.print_without_newline(re.sub(r'\s', '\xff', self.__bytes_to_printable_char(self.__wire_format[self.__position - 8 : self.__position])))
        """
        if idx != len:
            NdnTlvPrinter.print_without_newline("\t".expandtabs(50 + (8 - idx % 8) * 3 - 3 * self.__indention_level))
        """
        NdnTlvPrinter.print_without_newline("\t".expandtabs(50 + (8 - idx % 8) * 3 - 3 * self.__indention_level))
        NdnTlvPrinter.print_without_newline(re.sub(r'\s', '\x00', self.__bytes_to_printable_char(self.__wire_format[self.__position - (idx % 8): self.__position])))
        #print("<<test>>")
