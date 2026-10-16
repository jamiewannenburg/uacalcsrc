# coding: utf-8
# Dual-runtime parity script for leftover conlat types.
from __future__ import print_function

from org.uacalc.alg.conlat import (
    BasicBinaryRelation,
    BasicPartition,
    CentralityData,
    Polymorphisms,
    Subtrace,
    TypeFinder,
)
from org.uacalc.io import AlgebraIO
from org.uacalc.util import IntArray


def _ia(obj):
    if obj is None:
        return None
    try:
        return [int(x) for x in list(obj)]
    except TypeError:
        pass
    for attr in ("getArray", "get_array", "toArray", "to_array"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            return [int(x) for x in fn()]
    return str(obj)


def test():
    st = Subtrace(0, 1, True)
    print("st=" + st.toString())
    print("st_brief=" + st.toString(True))
    print("st_first=" + str(st.first()))
    print("st_second=" + str(st.second()))
    print("st_type=" + str(st.type()))
    print("st_inv=" + str(st.hasInvolution()))
    st.setType(2)
    print("st_set_type=" + str(st.type()))
    st.setSubtraceUniverse([IntArray([0, 1]), IntArray([1, 0])])
    su = st.getSubtraceUniverse()
    print("st_su=" + str([_ia(p) for p in list(su)]))
    st.setMatrixUniverse([IntArray([0, 0, 1, 1])])
    print("st_mu=" + str([_ia(p) for p in list(st.getMatrixUniverse())]))

    rel = BasicBinaryRelation(3)
    rel.add(0, 1)
    rel.add(0, 2)
    print("bbr=" + rel.toString())
    print("bbr_univ=" + str(rel.universeSize()))
    print("bbr_rel=" + str(rel.isRelated(0, 1)))
    print("bbr_pairs=" + str([_ia(p) for p in list(rel.getPairs())]))
    print("bbr_refl=" + str(rel.isReflexive()))
    print("bbr_sym=" + str(rel.isSymmetric()))
    ident = BasicBinaryRelation.identity(3)
    print("bbr_id=" + ident.toString())
    beta = BasicBinaryRelation(3)
    beta.add(1, 0)
    print("bbr_compose=" + rel.compose(beta).toString())
    print("bbr_cmp=" + str(rel.compareTo(ident)))

    cd = CentralityData(ident, ident, BasicPartition.zero(3))
    print("cd_left=" + cd.getLeft().toString())
    print("cd_right=" + cd.getRight().toString())
    print("cd_delta=" + str(cd.getDelta()))
    print("cd_cmp=" + str(cd.compareTo(cd)))
    print("cd_str=" + cd.toString())
    cd.setCentralityFailure(None)
    cd.setWeakCentralityFailure(None)
    cd.setStrongRectangularityFailure(None)
    print("cd_fail=" + str(cd.getCentralityFailure()))
    print("cd_wfail=" + str(cd.getWeakCentralityFailure()))
    print("cd_sfail=" + str(cd.getStrongRectangularityFailure()))

    poly = Polymorphisms(1, [BasicPartition.zero(2)], True, None)
    print("poly_ok=" + str(poly is not None))

    alg = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    tf = TypeFinder(alg)
    tf.init()
    print("tf_types=" + str(sorted(list(tf.findTypeSet()))))
    jis = list(alg.con().joinIrreducibles())
    beta_p = jis[0]
    stf = tf.findSubtrace(beta_p)
    print("tf_sub=" + stf.toString())
    print("tf_type=" + str(tf.findType(beta_p)))
    gp = alg.con().generatingPair(beta_p)
    print("tf_is_sub=" + str(tf.isSubtrace(gp, beta_p)))
    try:
        tf.nextPairForSubtrace(IntArray([0, 1]), None, None, None)
        print("tf_next=ran")
    except Exception:
        import sys
        print("tf_next=" + type(sys.exc_info()[1]).__name__)
    except:
        import sys
        err = sys.exc_info()[1]
        print("tf_next=" + type(err).__name__)


if __name__ == "__main__":
    test()
