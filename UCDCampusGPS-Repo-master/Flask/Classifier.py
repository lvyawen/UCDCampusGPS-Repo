import os
import urllib.request
import csv
import pandas as pd
import json
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import neighbors
import sys
import numpy as np
import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

text_digit_vals = {}
clf =0


#Function to handle non-numeric datas

def handle_non_numeric_data(df):
    columns = df.columns.values

    for column in columns:
        global text_digit_vals

        def convert_to_int(val):
            return text_digit_vals[val]

        if df[column].dtype != np.int64 or df[column] != np.float64:
            column_contents = df[column].values.tolist()
            unique_elements = set(column_contents)
            x = 0
            for unique in unique_elements:
                text_digit_vals[unique] = x
                x += 1

            df[column] = list(map(convert_to_int, df[column]))
    return df

#Clasiffier
def predict_classifier(routerobj):

    global clf
    pd.options.mode.chained_assignment = None;
    router_df = pd.DataFrame(routerobj);
    router_df.is_copy = False;
    router_df = router_df.ix[:, [11, 15, 0]];
#read the values of the router object from the database and form a dataframe and train the calssifier
    if (clf ==0):
        link = "https://search-indoor-navigation-r2fy6yafkgybvrrhsgpcdev62e.us-east-2.es.amazonaws.com/fingerprint/routers/_search?size=3000"
        response = urllib.request.urlopen(link)
        html = response.read().decode()
        formattedRequest = json.loads(html)
        header = ["id", "BSSID", "SSID", "room_num", "frequency", "level", "latitude1", "longitude1", "floor"]
        result = (formattedRequest['hits']['hits'])
        df = pd.DataFrame()
        for rows in result:
            SR_row = pd.Series(rows['_source'])
            df = df.append(SR_row, ignore_index=True)

        df_non_numeric = handle_non_numeric_data(df.ix[:, [0, 1, 7]])
        df_non_numeric.is_copy = False;

        df_numeric = df.ix[:, [2, 3, 4, 5, 6]]
        df_numeric.is_copy = False;
        df = df_numeric.join(df_non_numeric)
        X_classes = df.ix[:, [1, 3, 5]]
        y = df.ix[:, [2, 4]]
        X_classes.is_copy = False;
        y.is_copy = False;
        x_train, x_test, y_train, y_test = train_test_split(X_classes, y, test_size=.33, random_state=17)
        clf = neighbors.KNeighborsClassifier()
        clf.fit(x_train, y_train)
    # use the df getting from the req_json.
    count = 0;
    for val in router_df["BSSID"].values:
        if (val in text_digit_vals.keys()):
            val = text_digit_vals[val];
            router_df["BSSID"].values[count] = val;
            count = count + 1;
        else:
            router_df = router_df.drop([count]);

    lat = 0;
    long = 0;
    for index, row in router_df.iterrows():
       # have the integer check here
       try:
            lat = lat + float(clf.predict([router_df.iloc[index]])[0][0])
            long = long + float(clf.predict([router_df.iloc[index]])[0][1])
       except IndexError:
           print("out of bound");
    lat = lat/router_df.shape[0];
    long = long/router_df.shape[0];

    return str(lat)+","+str(long);
