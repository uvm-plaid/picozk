from libcpp cimport bool

cdef extern from "EMPBridge.cpp":
    pass

cdef extern from "EMPBridge.h" namespace "emp_bridge_cpp":
    void emp_setup_bool_zk(int)
    void emp_finish_bool_zk()
    void emp_setup_arith_zk(int)
    void emp_finish_arith_zk()

cdef extern from "emp-tool/emp-tool.h" namespace "emp":
    cdef cppclass Bit:
        Bit() except +
        Bit(bool, int) except +
        Bit operator&(Bit)
        bool reveal()

cdef extern from "emp-zk/emp-zk-arith/emp-zk-arith.h":
    cdef cppclass IntFp:
        IntFp() except +
        IntFp(unsigned long long, int) except +
        unsigned long long reveal()
        bool reveal(unsigned long long)
        IntFp negate()
        IntFp operator+(IntFp)
        IntFp operator*(IntFp)

