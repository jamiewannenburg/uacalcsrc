<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>W(S_3)</algName>
    <cardinality>8</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>arrow</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">7,7,7,7,7,7,7,7</row>
            <row r="[1]">0,3,3,3,6,6,6,7</row>
            <row r="[2]">0,1,2,3,4,5,6,7</row>
            <row r="[3]">0,1,1,3,4,4,6,7</row>
            <row r="[4]">0,0,0,0,3,3,3,7</row>
            <row r="[5]">0,0,0,0,1,2,3,7</row>
            <row r="[6]">0,0,0,0,1,1,3,7</row>
            <row r="[7]">0,0,0,0,0,0,0,7</row>
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
            <row r="[0]">0,0,0,0,0,0,0,0</row>
            <row r="[1]">0,1,1,1,4,4,4,7</row>
            <row r="[2]">0,1,2,3,4,5,6,7</row>
            <row r="[3]">0,1,3,3,4,6,6,7</row>
            <row r="[4]">0,4,4,4,7,7,7,7</row>
            <row r="[5]">0,4,5,6,7,7,7,7</row>
            <row r="[6]">0,4,6,6,7,7,7,7</row>
            <row r="[7]">0,7,7,7,7,7,7,7</row>
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
            <row r="[0]">0,1,2,3,4,5,6,7</row>
            <row r="[1]">1,1,2,3,4,5,6,7</row>
            <row r="[2]">2,2,2,3,5,5,6,7</row>
            <row r="[3]">3,3,3,3,6,6,6,7</row>
            <row r="[4]">4,4,5,6,4,5,6,7</row>
            <row r="[5]">5,5,5,6,5,5,6,7</row>
            <row r="[6]">6,6,6,6,6,6,6,7</row>
            <row r="[7]">7,7,7,7,7,7,7,7</row>
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
            <row r="[0]">0,0,0,0,0,0,0,0</row>
            <row r="[1]">0,1,1,1,1,1,1,1</row>
            <row r="[2]">0,1,2,2,1,2,2,2</row>
            <row r="[3]">0,1,2,3,1,2,3,3</row>
            <row r="[4]">0,1,1,1,4,4,4,4</row>
            <row r="[5]">0,1,2,2,4,5,5,5</row>
            <row r="[6]">0,1,2,3,4,5,6,6</row>
            <row r="[7]">0,1,2,3,4,5,6,7</row>
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
            <row>7,6,5,4,3,2,1,0</row>
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
            <row>2</row>
          </intArray>
        </opTable>
      </op>
    </operations>
  </basicAlgebra>
</algebra>
