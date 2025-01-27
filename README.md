<h1>GridFlexPy.py</h1>
<p align = "center">
<img src="img\logo.webp" width ="500" height="500"> 
</p>

<p style="text-indent: 20px; font-size: 20px ">
This work is a python framework to help researchers and users that want to run powerflux simulations and need simplifications to solve otimization problems. It's developed using Python and OpenDSS using the library <a href="https://github.com/dss-extensions/OpenDSSDirect.py" target="_blank">OpenDSSDirect.py</a>.
This work was developed during the program of  <b>Bolsa Estágio de Pesquisa no Exterior(BEPE)</b> sponsored by <a href="https://fapesp.br" target="_blank"> Fundação de Amparo à Pesquisa do Estado de São Paulo (FAPESP)</a> in Porto, Portugal at <b>Research Group on Intelligent Engineering and Computing for Advanced Innovation and Development (GECAD)</b> a unit settled in the <b>Institue of Egineering - Polytechnic of Porto (ISEP/IPP)</b>
</p>

<h2>Summary</h2>
<ol style="font-size: 20px ">
    <li>Introduction</li>
    <li>Features</li>
    <li>Directories</li>
    <li>How to Use</li>
</ol>
<hr>
<h3> 1.Introduction</h3>

<p style="text-indent: 20px; font-size: 20px ">
Python is a high-level programming language widely recognized for its versatility, ease of use, and extensive adoption in fields such as data science, machine learning, automation, and engineering. Due to its intuitive syntax and the support of a vast library of packages, Python has become the preferred choice for researchers and professionals seeking to develop robust and efficient solutions. Python is ideal for projects requiring the integration of diverse tools and ease of maintenance.
</p>

<p style="text-indent: 20px; font-size: 20px ">
OpenDSS is a tool for simulating electrical systems, with a particular focus on distribution networks. It supports power flow analysis, short-circuit studies, harmonic analysis, and renewable energy integration, enabling detailed and flexible modeling of complex electrical systems. Due to its script-based approach and capacity to handle large volumes of data, OpenDSS is widely used in both academic and industrial research.
</p>

<p style="text-indent: 20px; font-size: 20px ">
In this framework, the integration between Python and OpenDSS was achieved using the OpenDSSDirect library. This library provides a programmatic interface to the OpenDSS simulation engine, allowing full control over simulation parameters directly from Python scripts. Such integration enabled the development of a custom interface that facilitates data input, simulation execution, and result analysis. This allows the operation of batteries using the OpenDSS snapshot mode, which calculates an instantaneous power flow. In this mode, the integration with Python makes it possible to perform calculations and define the battery power for the next moment based on a specific operational mode.
</p>

<p style="text-indent: 20px;">
The interface usage is based on user input from an Excel spreadsheet containing information such as the start and end dates of the simulation, interval, details about the batteries present in the circuit, data on RED generators, load information, and public lighting in the case of a microgrid. Another input provided by the user is a file in .dss format, which contains all network information, including power data of feeders, transformers, as well as impedances and the geometry of distribution lines.
</p>


    
