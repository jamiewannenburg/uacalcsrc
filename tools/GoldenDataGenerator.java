import org.uacalc.io.*;
import org.uacalc.lat.*;
import org.uacalc.terms.*;
import org.uacalc.alg.*;
import java.io.*;
import java.util.*;

/**
 * Generate golden test data from Java UACalc.
 * Outputs JSON with expected results for parity testing.
 */
public class GoldenDataGenerator {
    
    public GoldenDataGenerator() {
    }
    
    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("Usage: java GoldenDataGenerator <package>");
            System.err.println("Packages: io, lat, terms");
            System.exit(1);
        }
        
        GoldenDataGenerator gen = new GoldenDataGenerator();
        String pkg = args[0];
        
        try {
            if ("io".equals(pkg)) {
                gen.generateIOGolden();
            } else if ("lat".equals(pkg)) {
                gen.generateLatGolden();
            } else if ("terms".equals(pkg)) {
                gen.generateTermsGolden();
            } else {
                System.err.println("Unknown package: " + pkg);
                System.exit(1);
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    private Map<String, Object> createMetadata(String pkg, int testCount) {
        Map<String, Object> meta = new LinkedHashMap<>();
        meta.put("package", "org.uacalc." + pkg);
        meta.put("generated_at", new Date().toString());
        meta.put("runtime", "java");
        meta.put("java_version", System.getProperty("java.version"));
        meta.put("test_cases", testCount);
        return meta;
    }
    
    private Map<String, Object> createTestCase(String id, String method, List<Object> args, 
                                                String description) {
        Map<String, Object> tc = new LinkedHashMap<>();
        tc.put("id", id);
        tc.put("method", method);
        tc.put("args", args);
        tc.put("kwargs", new HashMap<>());
        tc.put("description", description);
        return tc;
    }
    
    private Map<String, Object> createSuccessResult(Object returnValue, String stringRepr) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("success", true);
        result.put("return_value", serializeValue(returnValue));
        result.put("return_type", returnValue != null ? returnValue.getClass().getSimpleName() : "null");
        result.put("string_repr", stringRepr);
        return result;
    }
    
    private Map<String, Object> createErrorResult(Exception e) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("success", false);
        Map<String, Object> exc = new LinkedHashMap<>();
        exc.put("type", e.getClass().getSimpleName());
        exc.put("message", e.getMessage() != null ? e.getMessage() : "");
        result.put("exception", exc);
        return result;
    }
    
    private Object serializeValue(Object obj) {
        if (obj == null) return null;
        
        if (obj instanceof SmallAlgebra) {
            SmallAlgebra alg = (SmallAlgebra) obj;
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("__type__", "SmallAlgebra");
            map.put("name", alg.name());
            map.put("cardinality", alg.cardinality());
            List<org.uacalc.alg.op.Operation> ops = alg.operations();
            map.put("operation_count", ops != null ? ops.size() : 0);
            return map;
        }
        
        if (obj instanceof Lattice) {
            Lattice lat = (Lattice) obj;
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("__type__", "Lattice");
            map.put("cardinality", lat.cardinality());
            return map;
        }
        
        if (obj instanceof Term) {
            Term term = (Term) obj;
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("__type__", "Term");
            map.put("string", term.toString());
            return map;
        }
        
        // Primitives and strings
        return obj;
    }
    
    private void generateIOGolden() throws Exception {
        System.out.println("Generating golden data for org.uacalc.io...");
        
        List<Map<String, Object>> testCases = new ArrayList<>();
        
        // Test readAlgebraFile with various files
        String[] files = {"cyclic2.ua", "cyclic3.ua", "lat2.ua", "n5.ua"};
        for (String file : files) {
            String path = "resources/algebras/" + file;
            Map<String, Object> tc = createTestCase(
                "read_" + file.replace(".ua", ""),
                "AlgebraIO.readAlgebraFile",
                Arrays.asList(path),
                "Read " + file + " algebra from file"
            );
            
            try {
                SmallAlgebra alg = AlgebraIO.readAlgebraFile(path);
                tc.put("result", createSuccessResult(alg, alg.toString()));
            } catch (Exception e) {
                tc.put("result", createErrorResult(e));
            }
            
            testCases.add(tc);
        }
        
        // Test reading invalid file
        Map<String, Object> tcInvalid = createTestCase(
            "read_invalid",
            "AlgebraIO.readAlgebraFile",
            Arrays.asList("resources/algebras/invalid_parity.ua"),
            "Reading invalid file should raise BadAlgebraFileException"
        );
        try {
            AlgebraIO.readAlgebraFile("resources/algebras/invalid_parity.ua");
            tcInvalid.put("result", createSuccessResult(null, ""));
        } catch (Exception e) {
            tcInvalid.put("result", createErrorResult(e));
        }
        testCases.add(tcInvalid);
        
        // Test reading nonexistent file
        Map<String, Object> tcNonexist = createTestCase(
            "read_nonexistent",
            "AlgebraIO.readAlgebraFile",
            Arrays.asList("resources/algebras/nonexistent.ua"),
            "Reading nonexistent file should raise exception"
        );
        try {
            AlgebraIO.readAlgebraFile("resources/algebras/nonexistent.ua");
            tcNonexist.put("result", createSuccessResult(null, ""));
        } catch (Exception e) {
            tcNonexist.put("result", createErrorResult(e));
        }
        testCases.add(tcNonexist);
        
        // Output JSON manually
        outputJSON(createMetadata("io", testCases.size()), testCases);
    }
    
    private void outputJSON(Map<String, Object> metadata, List<Map<String, Object>> testCases) {
        System.out.println("{");
        System.out.println("  \"metadata\": {");
        System.out.print("    \"package\": \"" + metadata.get("package") + "\",");
        System.out.print("    \"generated_at\": \"" + metadata.get("generated_at") + "\",");
        System.out.print("    \"runtime\": \"" + metadata.get("runtime") + "\",");
        System.out.print("    \"java_version\": \"" + metadata.get("java_version") + "\",");
        System.out.println("    \"test_cases\": " + metadata.get("test_cases"));
        System.out.println("  },");
        System.out.println("  \"test_cases\": [");
        
        for (int i = 0; i < testCases.size(); i++) {
            Map<String, Object> tc = testCases.get(i);
            System.out.println("    {");
            System.out.println("      \"id\": \"" + tc.get("id") + "\",");
            System.out.println("      \"method\": \"" + tc.get("method") + "\",");
            System.out.println("      \"args\": " + formatArgs((List)tc.get("args")) + ",");
            System.out.println("      \"kwargs\": {},");
            System.out.println("      \"description\": \"" + escapeJson((String)tc.get("description")) + "\",");
            System.out.println("      \"result\": " + formatResult((Map)tc.get("result")));
            if (tc.containsKey("skip_string_check")) {
                System.out.println("      ,\"skip_string_check\": true");
            }
            System.out.print("    }");
            if (i < testCases.size() - 1) System.out.println(",");
            else System.out.println();
        }
        
        System.out.println("  ]");
        System.out.println("}");
    }
    
    private String escapeJson(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }
    
    private String formatArgs(List args) {
        if (args == null || args.isEmpty()) return "[]";
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < args.size(); i++) {
            Object arg = args.get(i);
            if (arg instanceof String) {
                sb.append("\"").append(escapeJson((String)arg)).append("\"");
            } else if (arg instanceof int[][]) {
                sb.append(format2DArray((int[][])arg));
            } else {
                sb.append(arg);
            }
            if (i < args.size() - 1) sb.append(", ");
        }
        sb.append("]");
        return sb.toString();
    }
    
    private String format2DArray(int[][] arr) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < arr.length; i++) {
            sb.append("[");
            for (int j = 0; j < arr[i].length; j++) {
                sb.append(arr[i][j]);
                if (j < arr[i].length - 1) sb.append(", ");
            }
            sb.append("]");
            if (i < arr.length - 1) sb.append(", ");
        }
        sb.append("]");
        return sb.toString();
    }
    
    private String formatResult(Map result) {
        StringBuilder sb = new StringBuilder("{\n");
        sb.append("        \"success\": ").append(result.get("success"));
        
        if ((Boolean)result.get("success")) {
            sb.append(",\n        \"return_value\": ").append(formatValue(result.get("return_value")));
            sb.append(",\n        \"return_type\": \"").append(result.get("return_type")).append("\"");
            sb.append(",\n        \"string_repr\": \"").append(escapeJson((String)result.get("string_repr"))).append("\"");
        } else {
            Map exc = (Map)result.get("exception");
            sb.append(",\n        \"exception\": {\n");
            sb.append("          \"type\": \"").append(exc.get("type")).append("\",\n");
            sb.append("          \"message\": \"").append(escapeJson((String)exc.get("message"))).append("\"\n");
            sb.append("        }");
        }
        
        sb.append("\n      }");
        return sb.toString();
    }
    
    private String formatValue(Object obj) {
        if (obj == null) return "null";
        if (obj instanceof Map) {
            Map map = (Map)obj;
            StringBuilder sb = new StringBuilder("{\n");
            Object[] keys = map.keySet().toArray();
            for (int i = 0; i < keys.length; i++) {
                String key = (String)keys[i];
                sb.append("          \"").append(key).append("\": ");
                Object val = map.get(key);
                if (val instanceof String) {
                    sb.append("\"").append(escapeJson((String)val)).append("\"");
                } else {
                    sb.append(val);
                }
                if (i < keys.length - 1) sb.append(",");
                sb.append("\n");
            }
            sb.append("        }");
            return sb.toString();
        }
        return obj.toString();
    }
    
    private void generateLatGolden() throws Exception {
        System.out.println("Generating golden data for org.uacalc.lat...");
        
        List<Map<String, Object>> testCases = new ArrayList<>();
        
        // Test latticeFromJoin with 2-element chain
        int[][] join2 = {{0, 1}, {1, 1}};
        Map<String, Object> tc1 = createTestCase(
            "lattice_from_join_2chain",
            "Lattices.latticeFromJoin",
            Arrays.asList((Object) join2),
            "Build 2-element chain from join table"
        );
        try {
            Lattice lat = Lattices.latticeFromJoin(join2);
            tc1.put("result", createSuccessResult(lat, lat.toString()));
            tc1.put("skip_string_check", true);
        } catch (Exception e) {
            tc1.put("result", createErrorResult(e));
        }
        testCases.add(tc1);
        
        // Test latticeFromMeet with 2-element chain
        int[][] meet2 = {{0, 0}, {0, 1}};
        Map<String, Object> tc2 = createTestCase(
            "lattice_from_meet_2chain",
            "Lattices.latticeFromMeet",
            Arrays.asList((Object) meet2),
            "Build 2-element chain from meet table"
        );
        try {
            Lattice lat = Lattices.latticeFromMeet(meet2);
            tc2.put("result", createSuccessResult(lat, lat.toString()));
            tc2.put("skip_string_check", true);
        } catch (Exception e) {
            tc2.put("result", createErrorResult(e));
        }
        testCases.add(tc2);
        
        // Test latticeFromJoin with diamond M3
        int[][] joinDiamond = {
            {0, 3, 3, 3},
            {3, 1, 3, 3},
            {3, 3, 2, 3},
            {3, 3, 3, 3}
        };
        Map<String, Object> tc3 = createTestCase(
            "lattice_from_join_diamond",
            "Lattices.latticeFromJoin",
            Arrays.asList((Object) joinDiamond),
            "Build diamond lattice M3 from join table"
        );
        try {
            Lattice lat = Lattices.latticeFromJoin(joinDiamond);
            tc3.put("result", createSuccessResult(lat, lat.toString()));
            tc3.put("skip_string_check", true);
        } catch (Exception e) {
            tc3.put("result", createErrorResult(e));
        }
        testCases.add(tc3);
        
        // Output JSON
        outputJSON(createMetadata("lat", testCases.size()), testCases);
    }
    
    private void generateTermsGolden() throws Exception {
        System.out.println("Generating golden data for org.uacalc.terms...");
        
        List<Map<String, Object>> testCases = new ArrayList<>();
        
        // Test stringToTerm with various inputs
        String[] termStrings = {"x0", "f(x0)", "+(x0,x1)", "f(g(x0,x1))"};
        String[] ids = {"string_to_term_variable", "string_to_term_unary_op", 
                       "string_to_term_binary_op", "string_to_term_nested"};
        String[] descs = {"Parse a variable term", "Parse a term with unary operation",
                         "Parse a term with binary operation", "Parse a nested term"};
        
        for (int i = 0; i < termStrings.length; i++) {
            Map<String, Object> tc = createTestCase(
                ids[i],
                "Terms.stringToTerm",
                Arrays.asList(termStrings[i]),
                descs[i]
            );
            
            try {
                Term term = Terms.stringToTerm(termStrings[i]);
                tc.put("result", createSuccessResult(term, term.toString()));
            } catch (Exception e) {
                tc.put("result", createErrorResult(e));
            }
            
            testCases.add(tc);
        }
        
        // Test makeConstantTerm
        int[] constants = {0, 5};
        for (int val : constants) {
            Map<String, Object> tc = createTestCase(
                "make_constant_term_" + val,
                "NonVariableTerm.makeConstantTerm",
                Arrays.asList(val),
                "Create constant term for value " + val
            );
            
            try {
                Term term = NonVariableTerm.makeConstantTerm(val);
                tc.put("result", createSuccessResult(term, term.toString()));
            } catch (Exception e) {
                tc.put("result", createErrorResult(e));
            }
            
            testCases.add(tc);
        }
        
        // Output JSON
        outputJSON(createMetadata("terms", testCases.size()), testCases);
    }
}
