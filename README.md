# HCDE 310 Final Project: Campaign Finance Data Visualizations
**By Maya Sioson**

This code is used to generate data visualizations about presidential campaign finances for the 2020 election. Pictures of the final visualizations are included in the imgs folder.

### Data
Data is taken from the Federal Election Commission (FEC). An API key can be obtained [here](https://api.data.gov/signup/). The API's documentation is available [here](https://api.open.fec.gov/developers/).

Specifically, the visualizations are generated from itemized contributions to presidential candidates reported by their primary campaign committees. For each candidate, only the 1000 largest contributions were extracted and used to make the visualizations.

### Viewing/Regenerating the Visualizations
The final visualizations are included as .png images. There's also a .html file that includes all visualizations as well as context about them. It's unnecessary to run the code to view the visualizations, but they can be regenerated to include the most recent data by running (in order) `dataprocessing_fec.py`, `analysis.R`, and `visualizations.Rmd`. This will regenerate the `visualizations.html` file.

### Video Demo
A video demo explaining this project is available [here](https://youtu.be/haxibDYuWbE).
