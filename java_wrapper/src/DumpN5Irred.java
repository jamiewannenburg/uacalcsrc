import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import org.latdraw.orderedset.POElem;
import org.uacalc.alg.SmallAlgebra;
import org.uacalc.alg.conlat.BasicPartition;
import org.uacalc.alg.conlat.CongruenceLattice;
import org.uacalc.alg.conlat.Partition;
import org.uacalc.io.AlgebraIO;
import org.uacalc.lat.BasicLattice;

/**
 * Dump join/meet irreducibles of BasicLattice built from a congruence lattice.
 * Prints sorted canonical block forms (one per line) under JOIN_IRREDUCIBLES and
 * MEET_IRREDUCIBLES headers.
 */
public class DumpN5Irred {

    static String canonical(Partition p) {
        int[][] blocks = ((BasicPartition) p).getBlocks();
        List<String> blockStrs = new ArrayList<>();
        for (int[] block : blocks) {
            int[] sorted = block.clone();
            Arrays.sort(sorted);
            blockStrs.add(Arrays.toString(sorted));
        }
        Collections.sort(blockStrs);
        return String.join("|", blockStrs);
    }

    static void dumpSection(String header, List<POElem> elems) {
        System.out.println(header);
        List<String> canon = new ArrayList<>();
        for (POElem elem : elems) {
            Partition p = (Partition) elem.getUnderlyingObject();
            canon.add(canonical(p));
        }
        Collections.sort(canon);
        for (String s : canon) {
            System.out.println(s);
        }
    }

    public static void main(String[] args) throws Exception {
        String path = args.length > 0 ? args[0] : "resources/algebras/n5.ua";
        SmallAlgebra alg = AlgebraIO.readAlgebraFile(path);
        CongruenceLattice conLat = new CongruenceLattice(alg);
        BasicLattice lat = new BasicLattice("n5", conLat, false);

        @SuppressWarnings("unchecked")
        List<POElem> jis = lat.joinIrreducibles();
        dumpSection("JOIN_IRREDUCIBLES", jis);

        @SuppressWarnings("unchecked")
        List<POElem> mis = lat.meetIrreducibles();
        dumpSection("MEET_IRREDUCIBLES", mis);
    }
}