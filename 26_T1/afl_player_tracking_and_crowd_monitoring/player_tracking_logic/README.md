\# AFL Player Tracking Logic



This folder contains scripts developed for the Redback Project AFL Player Tracking system.  

These scripts support syncing, merging, evaluating, and analyzing AFL player tracking and event data.



\## 📂 Scripts



\- \*\*annotation\_converter.py\*\*  

&nbsp; Converts annotation formats into a consistent structure for further processing.



\- \*\*annotation\_sync.py\*\*  

&nbsp; Syncs manual event annotations with YOLOv8 + DeepSORT tracking outputs.



\- \*\*event\_timing\_analysis.py\*\*  

&nbsp; Analyzes and visualizes the timing of events across match footage.



\- \*\*merge\_synced.py\*\*  

&nbsp; Merges multiple synced annotation files into a single dataset.



\- \*\*prediction\_vs\_truth.py\*\*  

&nbsp; Evaluates predicted events against ground truth annotations, producing precision/recall metrics.



---



\## Usage



Each script can be run independently from the command line:



```bash

python annotation\_converter.py <input\_file> <output\_file>

python annotation\_sync.py <tracking\_file> <annotation\_file> <output\_file>

python event\_timing\_analysis.py <synced\_file> <output\_directory>

python merge\_synced.py <synced\_directory> <merged\_output\_file>

python prediction\_vs\_truth.py <predicted\_file> <truth\_file> <output\_report>





\## Notes



\- Replace `<...>` placeholders with the actual file paths and directories you are using.  

\- Ensure that output directories exist before running scripts (create them with `mkdir` if necessary).  

\- Scripts can be run independently, but together they form a full pipeline for syncing, merging, evaluating, and analyzing AFL tracking + event data.





\## Author



Developed by \*\*Jarrod Gillingham\*\* for \*Redback Project 4 – Player Tracking Logic / Integration \& Evaluation Team\*.







