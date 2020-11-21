# CSE6242

DESCRIPTION

INSTALLATION

findPlayersWithTargets.ipynb - Run this code on Kaggle to acquire the dataset on Kaggle. This will hold every play and calculate other features used for analysis. The csv output from this will be used to join with the openness calculation.

implement.ipynb - This notebook creates the Random Forest used to predict target probability. It takes the csv from findPlayersWithTargets.ipynb then joins it to the openness data. In the end, it binds the results so they can be used for analysis. It also creates a dataframe of who each QB was on each play, which is used for analysis.

summarise_model.ipynb - Joins files from implement.ipynb to create summary tables and dataframes which are exported for data visualization.

viz_1.Rmd - creates visualizations from the data created in summarise_model.ipynb.

logisitc_and_viz.Rmd - Creates logistic regression models and visualizations.

EXECUTION
