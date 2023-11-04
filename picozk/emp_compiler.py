from dataclasses import dataclass
from typing import List
import functools
from picozk.wire import *
from picozk.binary_int import BinaryInt
from picozk import config
from picozk.compiler import *

# g++ -pthread -Wall -funroll-loops -Wno-ignored-attributes -Wno-unused-result -march=native -maes -mrdseed -std=c++11 -O3 picozk_test.cpp -lemp-zk -lemp-tool -lcrypto -o picozk_test

class PicoZKEMPCompiler(PicoZKCompiler):
    def emit_call(self, call, *args):
        raise Exception('unsupported')

    def emit_gate(self, gate, *args, effect=False, field=None):
        if field is None:
            type_arg = 0
        else:
            type_arg = self.fields.index(field)

        ops = {'add': '+', 'addc': '+', 'mul': '*', 'mulc': '*'}

        if effect:
            if gate == 'assert_zero':
                assert len(args) == 1
                self.emit(f'  {args[0]}.reveal(0);')
            else:
                raise Exception('unknown gate:', gate)
            return
        else:
            a, b = args
            r = self.next_wire()
            if gate == 'addc' or gate == 'mulc':
                b = b.replace('<', '').replace('>', '')
            self.emit(f'  IntFp {r} = {a} {ops[gate]} {b};')
            return r

    def allocate(self, n, field=None):
        raise Exception('unsupported')

    def add_to_witness(self, x, field):
        if field == None:
            field_type = 0
            field = self.fields[field_type]
        else:
            field_type = self.fields.index(field)

        x = int(x)
        assert x % field == x

        r = self.next_wire()
        self.emit(f'  witness >> wit_val;')
        #self.emit(f'  std::cout << "WITNESS: " << wit_val << std::endl;')
        self.emit(f'  IntFp {r}(wit_val, ALICE);')
        self.witness_file.write(f'{x}\n')

        if field == 2:
            return BinaryWire(r, x, 2)
        else:
            return ArithmeticWire(r, x, field)

    def add_to_instance(self, x, field):
        raise Exception('unsupported')

    def constant_wire(self, e):
        raise Exception('unsupported')

    def next_wire(self):
        r = self.current_wire
        self.current_wire += 1
        return 'wire_' + str(r)

    def __enter__(self):
        global cc
        config.cc = self
        cc = self

        self.witness_file = open(self.file_prefix + '.wit', 'w')
        self.relation_file = open(self.file_prefix + '.cpp', 'w')

        self.relation_file.write(_emp_top)


    def __exit__(self, exception_type, exception_value, traceback):
        config.cc = None

        self.relation_file.write(_emp_end)

        self.witness_file.close()
        self.relation_file.close()


_emp_top = """
#include "emp-tool/emp-tool.h"
#include "emp-zk/emp-zk-arith/emp-zk-arith.h"
#include <iostream>
using namespace emp;
using namespace std;

int port, party;
const int threads = 1;

void run_zk(BoolIO<NetIO> *ios[threads], int party) {
  std::cout << "starting ZK proof" << std::endl;

  std::fstream witness("picozk_test.wit", std::ios_base::in);
  uint64_t wit_val;

  setup_zk_arith<BoolIO<NetIO>>(ios, threads, party);

"""

_emp_end = """

  finalize_zk_arith<BoolIO<NetIO>>();
  std::cout << "finished ZK proof" << std::endl;
}

int main(int argc, char **argv) {
  parse_party_and_port(argv, &party, &port);
  BoolIO<NetIO> *ios[threads];
  for (int i = 0; i < threads; ++i)
    ios[i] = new BoolIO<NetIO>(
        new NetIO(party == ALICE ? nullptr : "127.0.0.1", port + i),
        party == ALICE);

  run_zk(ios, party);

  for (int i = 0; i < threads; ++i) {
    delete ios[i]->io;
    delete ios[i];
  }
  return 0;
}
"""
