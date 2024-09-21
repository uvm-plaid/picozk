#include <iostream>
#include "EMPBridge.h"

#include <cstddef>
#include <cstdint>

#include <emp-tool/emp-tool.h>
#include <emp-zk/emp-zk.h>

using std::int64_t;
using std::size_t;
using namespace emp;



namespace emp_bridge_cpp {
  const int threads = 1;
  const int port = 12345;
  BoolIO<NetIO>* ios[threads];

  void emp_setup_bool_zk(int party) {
    for(int i = 0; i < threads; ++i)
      ios[i] = new BoolIO<NetIO>(new NetIO(party == ALICE?nullptr:"127.0.0.1",port+i), party==ALICE);
    setup_zk_bool<BoolIO<NetIO>>(ios, threads, party);
  }

  void emp_finish_bool_zk() {
    bool cheat = finalize_zk_bool<BoolIO<NetIO>>();
    if(cheat)error("cheat!\n");
    for (int i = 0; i < threads; ++i) {
      delete ios[i]->io;
      delete ios[i];
    }
  }

  void emp_setup_arith_zk(int party) {
    for (int i = 0; i < threads; ++i)
      ios[i] = new BoolIO<NetIO>(new NetIO(party == ALICE ? nullptr : "127.0.0.1", port + i),
                                 party == ALICE);
    setup_zk_arith<BoolIO<NetIO>>(ios, threads, party);
  }

  void emp_finish_arith_zk() {
    for (int i = 0; i < threads; ++i) {
      delete ios[i]->io;
      delete ios[i];
    }
  }

}
