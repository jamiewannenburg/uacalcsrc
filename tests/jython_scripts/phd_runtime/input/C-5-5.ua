<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>C-{5}-{5}</algName>
    <cardinality>5</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>arrow</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">4,4,4,4,4</row>
            <row r="[1]">0,1,2,3,4</row>
            <row r="[2]">0,0,2,2,4</row>
            <row r="[3]">0,0,0,1,4</row>
            <row r="[4]">0,0,0,0,4</row>
          </intArray>
        </opTable>
      </op>
      <op>
        <opSymbol>
          <opName>dot</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">0,0,0,0,0</row>
            <row r="[1]">0,1,2,3,4</row>
            <row r="[2]">0,2,2,4,4</row>
            <row r="[3]">0,3,4,4,4</row>
            <row r="[4]">0,4,4,4,4</row>
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
            <row r="[0]">0,1,2,3,4</row>
            <row r="[1]">1,1,2,3,4</row>
            <row r="[2]">2,2,2,3,4</row>
            <row r="[3]">3,3,3,3,4</row>
            <row r="[4]">4,4,4,4,4</row>
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
            <row r="[0]">0,0,0,0,0</row>
            <row r="[1]">0,1,1,1,1</row>
            <row r="[2]">0,1,2,2,2</row>
            <row r="[3]">0,1,2,3,3</row>
            <row r="[4]">0,1,2,3,4</row>
          </intArray>
        </opTable>
      </op>
      <op>
        <opSymbol>
          <opName>neg</opName>
          <arity>1</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row>4,3,2,1,0</row>
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
