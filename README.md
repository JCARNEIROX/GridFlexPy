<h1>GridFlexPy.py</h1>
<p align = "center">
<img src="img\logo.webp" width ="500" height="500"> 
</p>

<p style="text-indent: 20px; font-size: 20px ">
This work is a python framework to help researchers and users that want to run powerflux simulations and need simplifications to solve otimization problems. It's developed using Python and OpenDSS using the library <a href="https://github.com/dss-extensions/OpenDSSDirect.py" target="_blank"><b>OpenDSSDirect.py</b></a>.
This work was developed during the program of  <b>Bolsa Estágio de Pesquisa no Exterior(BEPE)</b> sponsored by <a href="https://fapesp.br" target="_blank"><b>Fundação de Amparo à Pesquisa do Estado de São Paulo (FAPESP)</b></a> in Porto, Portugal at <a href="https://www.gecad.isep.ipp.pt/"><b>Research Group on Intelligent Engineering and Computing for Advanced Innovation and Development (GECAD)</b></a> a unit settled in the <b>Institue of Egineering - Polytechnic of Porto (ISEP/IPP)</b>. The project was supervised by <a href="https://www.dsee.fee.unicamp.br/~mjrider/"><b>Marcos J. Rider</b></a> from <a href="https://unicamp.br/"><b>University of State of Campinas (UNICAMP)</b></a> and <a href="https://www.cienciavitae.pt/1612-8EA8-D0E8"><b>João André P. Soares</b></a> from GECAD.
</p>

<h2>Summary</h2>
<ol style="font-size: 20px ">
    <li>Introduction</li>
    <li>Features and Directories</li>
    <li>How to Use</li>
    <li>Contribution</li>
    <li>License</li>
    <li>Contacts</li>
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

<p style="text-indent: 20px; font-size: 20px ">
The interface usage is based on user input from an Excel spreadsheet containing information such as the start and end dates of the simulation, interval, details about the batteries present in the circuit, data on RED generators, load information, and public lighting in the case of a microgrid. Another input provided by the user is a file in .dss format, which contains all network information, including power data of feeders, transformers, as well as impedances and the geometry of distribution lines.
</p>

<h3> 2.Features</h3>
<p align = "left">
<img src="img\directories.png"> 
</p>

<p style="text-indent: 20px; font-size: 20px ">
The figure above shows how the directories of the framework are organized. In it, the "data" folder is intuitively separated into subfolders so that the user can quickly identify where each type of file they will use in their power flow should be placed, allowing the framework to access and perform the power flow. Inside the "spreadsheets" folder, there is a template spreadsheet, illustrated in Figure 2 below, so that the user can view and input the information about their circuit according to the established format. Similarly, the "dss_files" folder is where the .dss files are placed. Finally, in the "output" subfolder, all the results from the simulation will be stored. The framework returns to the user a total of 9 Comma-Separated Values (CSV) files, a widely used format due to its flexibility in manipulation and its efficiency in memory usage for large data volumes. These dataframes, as they are called, provide key information of interest for analysis in a power flow, such as: electrical power at each bus of the circuit, total demand load, total energy generation, demand supplied by the grid's input bus, electrical losses, power flow, current, and losses in the transmission lines between buses, voltage at each bus in the system in per unit (p.u.), a dataframe containing all battery information over time, such as identification, active and reactive power, energy, and State of Charge (SOC), and finally, a dataframe containing a time vector necessary for the data to be visualized in graphs, for example, using the Matplotlib library.
</p>

<h3> 3.How to Use</h3>
<p style="text-indent: 20px; font-size: 20px ">
The first step for the user to utilize the framework is to adapt the data to be used in the simulation according to the format of the example data already present in the directories, and place them in the appropriate directories. The user should then modify the information in the main.py file, adjusting the variables <b><i>name_spreadsheet</i></b>, <b><i>name_dss</i></b>, <b><i>kind</i></b>, and, if performing a power flow involving a <b>Battery Energy Storage System (BESS)</b>, modify the <b><i>bess_bus</i></b> variable, which is responsible for allocating the battery to a bus in the network.
As this is an open-source framework, the battery operation functions can be modified in the <a href = "modules\bess.py">bess.py</a> module, and additional functions can be created to operate the battery according to the user's specific metrics.
</p>

<h3> 4.Contribution</h3>
<h3> 5.License</h3>
<p style="text-indent: 20px; font-size: 20px ">
This project is licensed by MIT License, see more in <a href="\LICENSE">LICENSE</a> file.
</p>

<h3> 6.Contacts</h3>
<p style="text-indent: 20px; font-size: 20px ">
<b>Autor:</b> João Victor Gomes Carneiro
</p>
<p style="text-indent: 20px; font-size: 20px ">
<b>Email:</b> j239738@dac.unicamp.br
</p>
<p style="text-indent: 20px; font-size: 20px ">
<b>Linkedin:</b> <a href="https://www.linkedin.com/in/jvcarneiro/">jvcarneiro</a>
</p>

<hr>
<p style="text-indent: 20px; font-size: 20px ">
<b>CoAutor:</b> Lucas Zenichi Terada
</p>
<p style="text-indent: 20px; font-size: 20px ">
<b>Email:</b> l182775@dac.unicamp.br
</p>
<p style="text-indent: 20px; font-size: 20px ">
<b>Linkedin:</b> <a href="https://www.linkedin.com/in/lucaszenichi/">lucaszenichi</a>
</p>




    
