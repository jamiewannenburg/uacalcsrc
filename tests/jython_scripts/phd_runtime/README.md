Install
-------

Installing python 2.7. In a conda prompt:

    conda create -n py27 python=2.7
	conda activate py27
	pip install virtualenv
	python -m virtualenv venv
	venv\Scripts\activate
	pip install pyparsing
	
Installing jython:

Download jython

	java -jar jython-installer-2.7.2.jar

Download pyparsing source files https://github.com/pyparsing/pyparsing/tree/pyparsing_2.4.x and run

	jython setup.py install


UACalc files
------------

This is a collection of programs to manipulate algebras using jython and the UACalc library
as well as some of the results obtained by these algorithms.
