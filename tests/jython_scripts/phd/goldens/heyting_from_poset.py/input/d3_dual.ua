<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>dual(d_3)_*</algName>
    <cardinality>6</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>arrow</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">1,1,1,1,1,1</row>
            <row r="[1]">0,1,2,3,4,5</row>
            <row r="[2]">0,1,1,3,3,1</row>
            <row r="[3]">0,1,2,1,2,1</row>
            <row r="[4]">0,1,1,1,1,1</row>
            <row r="[5]">0,1,2,3,4,1</row>
          </intArray>
        </opTable>
      </op>
      <op>
        <opSymbol>
          <opName>join</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,1,2,3,4,5</row>
            <row r="[1]">1,1,1,1,1,1</row>
            <row r="[2]">2,1,2,5,2,5</row>
            <row r="[3]">3,1,5,3,3,5</row>
            <row r="[4]">4,1,2,3,4,5</row>
            <row r="[5]">5,1,5,5,5,5</row>
          </intArray>
        </opTable>
      </op>
      <op>
        <opSymbol>
          <opName>meet</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,0,0,0,0,0</row>
            <row r="[1]">0,1,2,3,4,5</row>
            <row r="[2]">0,2,2,4,4,2</row>
            <row r="[3]">0,3,4,3,4,3</row>
            <row r="[4]">0,4,4,4,4,4</row>
            <row r="[5]">0,5,2,3,4,5</row>
          </intArray>
        </opTable>
      </op>
      <op>
        <opSymbol>
          <opName>bot</opName>
          <arity>0</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row>0</row>
          </intArray>
        </opTable>
      </op>
      <op>
        <opSymbol>
          <opName>e</opName>
          <arity>0</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row>1</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>
