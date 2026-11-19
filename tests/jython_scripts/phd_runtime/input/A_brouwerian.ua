<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>Prod of Br3 x Br2-basic</algName>
    <desc>Editable copy of A2 (Prod of Br3 x Br2)</desc>
    <cardinality>6</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>arrow</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">5,5,5,5,5,5</row>
            <row r="[1]">3,5,5,3,5,5</row>
            <row r="[2]">3,4,5,3,4,5</row>
            <row r="[3]">2,2,2,5,5,5</row>
            <row r="[4]">0,2,2,3,5,5</row>
            <row r="[5]">0,1,2,3,4,5</row>
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
            <row r="[1]">1,1,2,4,4,5</row>
            <row r="[2]">2,2,2,5,5,5</row>
            <row r="[3]">3,4,5,3,4,5</row>
            <row r="[4]">4,4,5,4,4,5</row>
            <row r="[5]">5,5,5,5,5,5</row>
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
            <row r="[1]">0,1,1,0,1,1</row>
            <row r="[2]">0,1,2,0,1,2</row>
            <row r="[3]">0,0,0,3,3,3</row>
            <row r="[4]">0,1,1,3,4,4</row>
            <row r="[5]">0,1,2,3,4,5</row>
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
            <row>5</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>
