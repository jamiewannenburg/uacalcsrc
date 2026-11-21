import java.util.Arrays;
import org.uacalc.alg.op.Operation;
import org.uacalc.alg.op.Operations;
import org.uacalc.util.Horner;
import org.uacalc.util.IntArray;

/**
 * Dump intValueAt and valueAt for Operations.makeCompositionOp(n, pow).
 *
 * Args: n pow ALL
 *    or n pow i,j i,j ...
 *
 * Also prints getTable() (null until makeTable) and the exception class from
 * makeTable. Java indexes that table with Horner base 2 and never allocates it.
 */
public class DumpComposition {

    static void dumpPair(Operation op, int n, int i, int j) {
        int iv = op.intValueAt(new int[] {i, j});
        int[] f = Horner.hornerInv(i, n, n);
        int[] g = Horner.hornerInv(j, n, n);
        IntArray image = (IntArray) op.valueAt(Arrays.asList(new IntArray(f), new IntArray(g)));
        int[] arr = image.getArray();
        StringBuilder sb = new StringBuilder();
        for (int k = 0; k < arr.length; k++) {
            if (k > 0) {
                sb.append(',');
            }
            sb.append(arr[k]);
        }
        System.out.println("INT " + i + " " + j + " " + iv);
        System.out.println("VAL " + i + " " + j + " " + sb);
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            throw new IllegalArgumentException("usage: DumpComposition n pow ALL | i,j ...");
        }
        int n = Integer.parseInt(args[0]);
        int pow = Integer.parseInt(args[1]);
        Operation op = Operations.makeCompositionOp(n, pow);
        int[] table = op.getTable();
        System.out.println(table == null ? "GET_TABLE null" : "GET_TABLE len=" + table.length);
        try {
            op.makeTable();
            int[] after = op.getTable();
            System.out.println(after == null ? "MAKE_TABLE null" : "MAKE_TABLE len=" + after.length);
        } catch (Throwable t) {
            System.out.println("MAKE_TABLE " + t.getClass().getName());
        }
        boolean all = args.length == 2 || "ALL".equals(args[2]);
        if (all) {
            for (int i = 0; i < pow; i++) {
                for (int j = 0; j < pow; j++) {
                    dumpPair(op, n, i, j);
                }
            }
            return;
        }
        for (int a = 2; a < args.length; a++) {
            String[] parts = args[a].split(",");
            dumpPair(op, n, Integer.parseInt(parts[0]), Integer.parseInt(parts[1]));
        }
    }
}
