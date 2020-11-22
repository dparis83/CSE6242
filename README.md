# CSE6242

DESCRIPTION

Our project utilizes tracking data from the NFL to evaluate Quarterback decision-making on pass plays. The data is publicly available at https://www.kaggle.com/c/nfl-big-data-bowl-2021, replication notebooks need to be run on Kaggle in some instances. Our package parses over 18 million frames from the tracking data, which records information every tenth of a second on every play. The data is from the 2018 season only.

The following notebooks filter the data into a more usable form, calculate our innovative metrics, then fits a few logisitc regression models and trains a Random Forest. Our process allows us to glean insights on Quarterback decision making, and which Quarterbacks throw to the most open receivers.

INSTALLATION

findPlayersWithTargets.ipynb - Run this code on Kaggle to acquire the dataset on Kaggle. This will hold every play and calculate other features used for analysis. The csv output from this will be used to join with the openness calculation.

implement.ipynb - This notebook creates the Random Forest used to predict target probability. It takes the csv from findPlayersWithTargets.ipynb then joins it to the openness data. In the end, it binds the results so they can be used for analysis. It also creates a dataframe of who each QB was on each play, which is used for analysis. This code was run in Google Colab.

summarise_model.ipynb - Joins files from implement.ipynb to create summary tables and dataframes which are exported for data visualization. This code was run in Google Colab.

viz_1.Rmd - creates visualizations from the data created in summarise_model.ipynb.

logisitc_and_viz.Rmd - Creates logistic regression models and visualizations.

EXECUTION
