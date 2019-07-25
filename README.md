# Model of Prediction Sales
Model of times series to make a forecast of 12 months of sector sales. The input is a xlsx file with sales data over five years in the passed and the output is a dataframe, but can be adapt to save in a csv file and graphics.

### Initial Settings
1 - In the service.py file in the root folder, in the first line, you need to configure the anacona environment itself.
>**Example:** #!/home/buzato/anaconda3/envs/py360/bin/python

2 - Install python libraries those are:
1. datetime
2. pandas
3. multiprocessing
4. numpy
5. sklearn
6. stantsmodels

### Run
** Command to help: ** ./service -h
** Command to execute: ** ./service -v -s portable -p 8
** Option Parameters: **
- v: verbose
- s: Forecasting sectors [portable | home | dressing room | technology]
- p: Parallel process number will be used
