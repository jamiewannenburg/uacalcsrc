<?xml version="1.0"?>
<algebra>
  <basicAlgebra>
    <algName>C_4</algName>
    <desc>The 0-generated 4-element De Morgan monoid (chain) with e less-than f</desc>
    <cardinality>4</cardinality>
    <operations>
      <op>
        <opSymbol>
          <opName>arrow</opName>
          <arity>2</arity>
        </opSymbol>
        <opTable>
          <intArray>
            <row r="[0]">3,3,3,3</row>
            <row r="[1]">0,1,2,3</row>
            <row r="[2]">0,0,1,3</row>
            <row r="[3]">0,0,0,3</row>
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
            <row r="[0]">0,0,0,0</row>
            <row r="[1]">0,1,2,3</row>
            <row r="[2]">0,2,3,3</row>
            <row r="[3]">0,3,3,3</row>
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
            <row r="[0]">0,1,2,3</row>
            <row r="[1]">1,1,2,3</row>
            <row r="[2]">2,2,2,3</row>
            <row r="[3]">3,3,3,3</row>
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
            <row r="[0]">0,0,0,0</row>
            <row r="[1]">0,1,1,1</row>
            <row r="[2]">0,1,2,2</row>
            <row r="[3]">0,1,2,3</row>
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
            <row>3,2,1,0</row>
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
