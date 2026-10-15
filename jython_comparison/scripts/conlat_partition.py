# coding: utf-8
# Dual-runtime parity script for Partition / BasicPartition / CongruenceLattice.
from __future__ import print_function

from org.uacalc.alg.conlat import BasicPartition, Partition, CongruenceLattice
from org.uacalc.io import AlgebraIO


def test():
    z = BasicPartition.zero(3)
    o = BasicPartition.one(3)
    p01 = BasicPartition("|0 1|2|")
    p12 = BasicPartition("|0|1 2|")
    print("zero=" + str(z))
    print("one=" + str(o))
    print("p01=" + str(p01))
    print("univ=" + str(p01.universeSize()))
    print("blocks=" + str(p01.numberOfBlocks()))
    print("related=" + str(p01.isRelated(0, 1)))
    print("rep=" + str(p01.representative(1)))
    print("join=" + str(p01.join(p12)))
    print("meet=" + str(p01.meet(p12)))
    print("leq=" + str(p01.leq(o)))
    print("arr=" + str(list(p01.toArray())))
    print("eq=" + str(p01.equals(BasicPartition(list(p01.toArray())))))
    print("kiss=" + BasicPartition.partToKissString(list(p01.toArray())))
    print("proj=" + str(BasicPartition.firstProjection(2)))
    print("hash=" + str(p01.hashCode()))
    payload = list(p01.toArray())
    txt = p01.toString()
    rt = BasicPartition(payload)
    rt2 = BasicPartition(txt)
    print("rt_eq=" + str(p01.equals(rt) and p01.equals(rt2)))
    print("rt_join=" + str(rt.join(p12)))
    print("rt_meet=" + str(rt.meet(p12)))
    print("rt_leq=" + str(rt.leq(o)))
    print("rt_str=" + str(rt))

    alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    con = CongruenceLattice(alg)
    print("con_card=" + str(con.cardinality()))
    print("con_name=" + str(con.getName()))
    print("con_zero=" + str(con.zero()))
    print("con_one=" + str(con.one()))
    print("con_join=" + str(con.join(con.zero(), con.one())))
    print("con_meet=" + str(con.meet(con.zero(), con.one())))
    print("con_leq=" + str(con.leq(con.zero(), con.one())))
    print("con_cg=" + str(con.Cg(0, 1)))
    print("PrintType_INTERNAL=" + str(Partition.PrintType.INTERNAL))


if __name__ == "__main__":
    test()
