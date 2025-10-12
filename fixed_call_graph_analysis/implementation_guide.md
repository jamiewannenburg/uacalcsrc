# UACalc Implementation Guide

This guide provides the correct order for implementing UACalc classes in Rust.

## Implementation Strategy

1. **Start with Level 0 classes** - These have no dependencies on other UACalc classes
2. **Work your way up** - Implement classes in dependency order
3. **Test each class** - Ensure each implementation works before moving to the next

## Current Status

### Already Implemented ✅
- org.uacalc.alg.conlat.Partition
- org.uacalc.alg.op.OperationSymbol
- org.uacalc.alg.op.SimilarityType
- org.uacalc.io.BadAlgebraFileException
- org.uacalc.io.ExtFileFilter
- org.uacalc.util.ArrayIncrementor
- org.uacalc.util.ArrayString
- org.uacalc.util.Horner
- org.uacalc.util.PermutationGenerator
- org.uacalc.util.SimpleList
- org.uacalc.util.virtuallist.LongList

### Next to Implement 🎯

**Priority 1: Level 0 Classes (No Dependencies)**

1. **org.uacalc.alg.AlgebraWithGeneratingVector**
   - No UACalc dependencies
   - Safe to implement immediately

2. **org.uacalc.alg.CloserTiming**
   - No UACalc dependencies
   - Safe to implement immediately

3. **org.uacalc.alg.Homomorphism**
   - No UACalc dependencies
   - Safe to implement immediately

4. **org.uacalc.alg.MaltsevProductDecomposition**
   - No UACalc dependencies
   - Safe to implement immediately

5. **org.uacalc.alg.conlat.BasicBinaryRelation**
   - No UACalc dependencies
   - Safe to implement immediately

6. **org.uacalc.alg.conlat.BinaryRelation**
   - No UACalc dependencies
   - Safe to implement immediately

7. **org.uacalc.alg.conlat.CentralityData**
   - No UACalc dependencies
   - Safe to implement immediately

8. **org.uacalc.alg.conlat.Polymorphisms**
   - No UACalc dependencies
   - Safe to implement immediately

9. **org.uacalc.alg.op.AbstractIntOperation**
   - No UACalc dependencies
   - Safe to implement immediately

10. **org.uacalc.alg.op.Operation**
   - No UACalc dependencies
   - Safe to implement immediately

## Complete Implementation Order

| Level | Class | Dependencies | Status |
|-------|-------|-------------|--------|
| 0 | org.uacalc.alg.AlgebraWithGeneratingVector | 0 | ⏳ Pending |
| 0 | org.uacalc.alg.CloserTiming | 0 | ⏳ Pending |
| 0 | org.uacalc.alg.Homomorphism | 0 | ⏳ Pending |
| 0 | org.uacalc.alg.MaltsevProductDecomposition | 0 | ⏳ Pending |
| 0 | org.uacalc.alg.conlat.BasicBinaryRelation | 0 | ⏳ Pending |
| 0 | org.uacalc.alg.conlat.BinaryRelation | 0 | ⏳ Pending |
| 0 | org.uacalc.alg.conlat.CentralityData | 0 | ⏳ Pending |
| 0 | org.uacalc.alg.conlat.Polymorphisms | 0 | ⏳ Pending |
| 0 | org.uacalc.alg.op.AbstractIntOperation | 0 | ⏳ Pending |
| 0 | org.uacalc.alg.op.Operation | 1 | ⏳ Pending |
| 0 | org.uacalc.alg.op.ParameterizedOperation | 0 | ⏳ Pending |
| 0 | org.uacalc.alg.parallel.Pool | 0 | ⏳ Pending |
| 0 | org.uacalc.alg.parallel.SingleClose | 0 | ⏳ Pending |
| 0 | org.uacalc.element.Element | 0 | ⏳ Pending |
| 0 | org.uacalc.element.SubProductElement | 0 | ⏳ Pending |
| 0 | org.uacalc.eq.Equation | 0 | ⏳ Pending |
| 0 | org.uacalc.eq.Equations | 0 | ⏳ Pending |
| 0 | org.uacalc.eq.Presentation | 0 | ⏳ Pending |
| 0 | org.uacalc.example.Average | 0 | ⏳ Pending |
| 0 | org.uacalc.example.FiniteField | 0 | ⏳ Pending |
| 0 | org.uacalc.example.Globals | 0 | ⏳ Pending |
| 0 | org.uacalc.example.HasConstantTuple | 0 | ⏳ Pending |
| 0 | org.uacalc.example.Jipsen | 0 | ⏳ Pending |
| 0 | org.uacalc.example.KKMVWExample | 0 | ⏳ Pending |
| 0 | org.uacalc.example.TupleStream | 0 | ⏳ Pending |
| 0 | org.uacalc.example.Type1 | 0 | ⏳ Pending |
| 0 | org.uacalc.fplat.PartiallyDefinedLattice | 0 | ⏳ Pending |
| 0 | org.uacalc.io.BadAlgebraFileException | 0 | ✅ Implemented |
| 0 | org.uacalc.io.Mace4Reader | 0 | ⏳ Pending |
| 0 | org.uacalc.lat.Lattice | 0 | ⏳ Pending |
| 0 | org.uacalc.lat.Lattices | 0 | ⏳ Pending |
| 0 | org.uacalc.lat.Order | 0 | ⏳ Pending |
| 0 | org.uacalc.lat.OrderedSets | 0 | ⏳ Pending |
| 0 | org.uacalc.lat.SmallLattice | 0 | ⏳ Pending |
| 0 | org.uacalc.nbui.AlgebraPreviewer | 0 | ⏳ Pending |
| 0 | org.uacalc.nbui.LatDrawer | 0 | ⏳ Pending |
| 0 | org.uacalc.nbui.PopupListener | 0 | ⏳ Pending |
| 0 | org.uacalc.nbui.UACalc | 0 | ⏳ Pending |
| 0 | org.uacalc.nbui.Version | 0 | ⏳ Pending |
| 0 | org.uacalc.terms.Variable | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.AlgebraEditor | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.AlgebraTableInputPanel | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.ComputationsPanel | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.LatDrawPanel | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.MonitorPanel | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.NewAlgebraDialog | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.PropertiesPanel | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.Tabs | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.table.AlgebraTableModel | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.table.AlgebraTablePanel | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.table.ConLatticeTableModel | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.table.IntegerEditor | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.table.LatticeTableModel | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.table.OperationInputTable | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.table.TableUtils | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.table.TaskTableModel | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.table.TermTableModel | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.table.TermTablePanel | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.tm.BackgroundExec | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.tm.GuiExecutor | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.tm.ProgressState | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.util.GUIAlgebra | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.util.GUIAlgebraList | 0 | ⏳ Pending |
| 0 | org.uacalc.ui.util.RandomGenerator | 0 | ⏳ Pending |
| 0 | org.uacalc.util.ArrayIncrementor | 0 | ✅ Implemented |
| 0 | org.uacalc.util.SequenceGenerator | 2 | ⏳ Pending |
| 0 | org.uacalc.util.virtuallist.LongList | 0 | ✅ Implemented |
| 0 | org.uacalc.util.virtuallist.TupleWithMin | 0 | ⏳ Pending |
| 0 | org.uacalc.util.virtuallist.VirtualLists | 0 | ⏳ Pending |
| 1 | org.uacalc.alg.AlgebraFromMinimalSets | 1 | ⏳ Pending |
| 1 | org.uacalc.alg.MaltsevDecompositionIterator | 1 | ⏳ Pending |
| 1 | org.uacalc.alg.ParameterizedAlgebra | 1 | ⏳ Pending |
| 1 | org.uacalc.alg.QuotientElement | 1 | ⏳ Pending |
| 1 | org.uacalc.alg.SmallAlgebra | 1 | ⏳ Pending |
| 1 | org.uacalc.alg.UnaryTermsMonoid | 1 | ⏳ Pending |
| 1 | org.uacalc.alg.conlat.Partition | 1 | ✅ Implemented |
| 1 | org.uacalc.alg.conlat.Subtrace | 1 | ⏳ Pending |
| 1 | org.uacalc.alg.conlat.to | 1 | ⏳ Pending |
| 1 | org.uacalc.alg.op.OperationSymbol | 1 | ✅ Implemented |
| 1 | org.uacalc.alg.op.Operations | 2 | ⏳ Pending |
| 1 | org.uacalc.alg.op.TermOperation | 1 | ⏳ Pending |
| 1 | org.uacalc.alg.op.TermOperationImp | 1 | ⏳ Pending |
| 1 | org.uacalc.alg.sublat.BasicSet | 1 | ⏳ Pending |
| 1 | org.uacalc.example.ConLyndonF3 | 1 | ⏳ Pending |
| 1 | org.uacalc.example.FilteringAlgebras | 1 | ⏳ Pending |
| 1 | org.uacalc.example.FinitelyPresentedAlg | 1 | ⏳ Pending |
| 1 | org.uacalc.example.Kearnes | 1 | ⏳ Pending |
| 1 | org.uacalc.example.MembershipTester | 1 | ⏳ Pending |
| 1 | org.uacalc.example.Michalewski | 1 | ⏳ Pending |
| 1 | org.uacalc.example.ParallelClose8 | 1 | ⏳ Pending |
| 1 | org.uacalc.group.PermutationGroup | 1 | ⏳ Pending |
| 1 | org.uacalc.io.AlgebraReader | 1 | ⏳ Pending |
| 1 | org.uacalc.io.AlgebraWriter | 1 | ⏳ Pending |
| 1 | org.uacalc.io.ExtFileFilter | 1 | ✅ Implemented |
| 1 | org.uacalc.io.JSONChannel | 1 | ⏳ Pending |
| 1 | org.uacalc.nbui.ConController | 1 | ⏳ Pending |
| 1 | org.uacalc.nbui.DrawingController | 1 | ⏳ Pending |
| 1 | org.uacalc.nbui.SubController | 1 | ⏳ Pending |
| 1 | org.uacalc.nbui.UACalculator2 | 1 | ⏳ Pending |
| 1 | org.uacalc.terms.Taylor | 1 | ⏳ Pending |
| 1 | org.uacalc.terms.Term | 1 | ⏳ Pending |
| 1 | org.uacalc.terms.Terms | 1 | ⏳ Pending |
| 1 | org.uacalc.terms.VariableImp | 1 | ⏳ Pending |
| 1 | org.uacalc.ui.table.ElemKeyTableModel | 1 | ⏳ Pending |
| 1 | org.uacalc.ui.tm.BackgroundTask | 1 | ⏳ Pending |
| 1 | org.uacalc.ui.util.WebBrowser | 1 | ⏳ Pending |
| 1 | org.uacalc.util.ArrayString | 1 | ✅ Implemented |
| 1 | org.uacalc.util.IntArray | 1 | ⏳ Pending |
| 1 | org.uacalc.util.SimpleList | 1 | ✅ Implemented |
| 2 | org.uacalc.alg.Algebra | 2 | ⏳ Pending |
| 2 | org.uacalc.alg.BasicAlgebra | 2 | ⏳ Pending |
| 2 | org.uacalc.alg.Closer | 2 | ⏳ Pending |
| 2 | org.uacalc.alg.GeneralAlgebra | 2 | ⏳ Pending |
| 2 | org.uacalc.alg.Malcev | 2 | ⏳ Pending |
| 2 | org.uacalc.alg.MatrixPowerAlgebra | 2 | ⏳ Pending |
| 2 | org.uacalc.alg.PolinLikeAlgebra | 2 | ⏳ Pending |
| 2 | org.uacalc.alg.PowerAlgebra | 2 | ⏳ Pending |
| 2 | org.uacalc.alg.op.AbstractOperation | 3 | ⏳ Pending |
| 2 | org.uacalc.alg.op.OperationWithDefaultValue | 2 | ⏳ Pending |
| 2 | org.uacalc.alg.op.SimilarityType | 2 | ✅ Implemented |
| 2 | org.uacalc.example.HasKaryNU | 2 | ⏳ Pending |
| 2 | org.uacalc.example.NoSymGroup | 2 | ⏳ Pending |
| 2 | org.uacalc.nbui.UACalculatorUI | 2 | ⏳ Pending |
| 2 | org.uacalc.ui.UACalculator | 2 | ⏳ Pending |
| 2 | org.uacalc.ui.tm.ProgressReport | 2 | ⏳ Pending |
| 2 | org.uacalc.util.Horner | 2 | ✅ Implemented |
| 2 | org.uacalc.util.PermutationGenerator | 2 | ✅ Implemented |
| 3 | org.uacalc.alg.ReductAlgebra | 3 | ⏳ Pending |
| 3 | org.uacalc.alg.conlat.CongruenceLattice | 3 | ⏳ Pending |
| 3 | org.uacalc.lat.BasicLattice | 3 | ⏳ Pending |
| 3 | org.uacalc.nbui.AlgebraEditorController | 3 | ⏳ Pending |
| 3 | org.uacalc.nbui.ComputationsController | 3 | ⏳ Pending |
| 3 | org.uacalc.terms.NonVariableTerm | 3 | ⏳ Pending |
| 4 | org.uacalc.alg.Algebras | 4 | ⏳ Pending |
| 4 | org.uacalc.alg.ProductAlgebra | 4 | ⏳ Pending |
| 4 | org.uacalc.alg.QuotientAlgebra | 4 | ⏳ Pending |
| 4 | org.uacalc.alg.SubProductAlgebra | 4 | ⏳ Pending |
| 4 | org.uacalc.alg.Subalgebra | 4 | ⏳ Pending |
| 4 | org.uacalc.alg.conlat.BasicPartition | 4 | ⏳ Pending |
| 4 | org.uacalc.alg.sublat.SubalgebraLattice | 4 | ⏳ Pending |
| 4 | org.uacalc.io.AlgebraIO | 4 | ⏳ Pending |
| 4 | org.uacalc.nbui.MainController | 4 | ⏳ Pending |
| 5 | org.uacalc.alg.BigProductAlgebra | 5 | ⏳ Pending |
| 5 | org.uacalc.alg.FreeAlgebra | 5 | ⏳ Pending |
| 5 | org.uacalc.ui.table.OperationTableModel | 5 | ⏳ Pending |
