from bitarray import bitarray
from bitarray import util
from PiCN.Layers.SynchronisationLayer.Hash import Murmurhash3
class InvertibleBloomFilter(object):
    def __init__(self, size):
        #ibf[][0] = keyIDSum ibf[][1] hash Sum ibf[][2] count
        self.ibf = [[0 for i in range(3)] for j in range(size)]
        self.hash_seed_list = [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9]

    #turn element key and value into bit representation so they can be XOR'd
    def input_to_bit(self, input):
        bit_key = bin(input)[2:]
        bit_value = ''.join(format(i, '08b') for i in bytearray(input, 'utf-8'))
        b =[]
        for i in bytearray("asd","utf-8"):
            for x in [int(d) for d in str(bin(i))[2:]]:
                b.append(x)
        result = ''
        for i in b:
            result += i
        return result
    #insert a new element into the IBF
    def insert_element(self, key, value):
        hash_list =[]
        bit_key = self.input_to_bit(key)
        bit_value = self.input_to_bit(value)
        for seed in self.hash_seed_list:
            hash_list.append(Murmurhash3.hash(key=bit_key, seed=seed))
        for entry in hash_list:
            #^ XORs an integer
            self.ibf[entry][0] = self.ibf[entry][0] ^ bit_key
            self.ibf[entry][1] = self.ibf[entry][0] ^ bit_value
            self.ibf[entry][2] += 1

    def remove_element(self, key, value):
        hash_list =[]
        for seed in self.hash_seed_list:
            hash_list.append(Murmurhash3.hash(key, value))
        for entry in hash_list:
            #^ XORs an integer
            self.ibf[entry][0] = self.ibf[entry][0] ^ key
            self.ibf[entry][1] = self.ibf[entry][0] ^ value
            self.ibf[entry][2] -= 1
    def compare(self, ibf, ibf2):
        for x in range(len(ibf)):
            if ibf[x][0] != ibf2[x][0] or ibf[x][1] != ibf2[x][1] or ibf[x][2] != ibf2[x][2]:
                return 0

