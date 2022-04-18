#!/usr/bin/env python
# coding: utf-8

# ## Step 1 : Load Libraries

# In[73]:


## Load Libraries
#
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn import metrics
from sklearn.preprocessing import LabelEncoder
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier


# ## Step 2 : Load Dataset

# In[74]:


dataset = pd.read_excel("Dataset/Sample.xlsx")
dataset.head()


# ## Step 3 : General Information Of Dataset 

# In[48]:


dataset.info()


# ## Step 4 : Preprocess Dataset

# ### A. Remove features and Rearrange features

# In[49]:


## Get All Feature Names
#
dataset.columns


# In[50]:


## Remove Unwanted Features
#
dataset = dataset.drop(columns = dataset.columns[[0, 1, 2, 3, 4, 7, 8]])


# In[51]:


## Interchange Features
#
dataset = dataset[["Submittal Description", "Submittal Type"]]
dataset.head()


# In[52]:


## Visualize count before filter
#
plt.figure(figsize = (20,8))
sns.countplot(data = dataset,
                x = 'Submittal Type')

plt.xticks(rotation = 90)
plt.show()


# In[53]:


## Fitler Dataset
#
options = ['Attic Stock', 'Calculations', 'Certificates', 'Color', 'Chart Delivery', 'Leed Requirements', 'Maintenance Data' , 'Manufacturer/Installation Cert',             'Mix Design', 'Mockups', 'MSDS', 'Owner Training', 'Product Data', 'Pre-Install Meeting Minutes', 'Procedures', 'Qualifications', 'Record Drawing',             'Reports', 'Samples', 'Schedules', 'Shop Drawings', 'Test Data', 'Warranty', 'Certifications']


# In[54]:


dataset = dataset[dataset['Submittal Type'].isin(options)]
dataset.head()


# In[55]:


## See the count
#
dataset.info()


# In[56]:


## Visualize count
#
sns.countplot(data = dataset,
                x = 'Submittal Type')

plt.xticks(rotation = 90)
plt.show()


# ### B. Encoding Feature

# In[57]:



labelencoder = LabelEncoder()
dataset['Submittal Type'] = labelencoder.fit_transform(dataset['Submittal Type'])


# In[58]:


dataset.head()


# ### C. Matrix of Feature

# In[59]:


X = dataset['Submittal Description']
Y = dataset['Submittal Type']


# ### D. Split Dataset

# In[60]:


X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.25, random_state = 0)


# ### E. Vectorization Encoding

# In[61]:


vectorizer = TfidfVectorizer()
X_train_tfidf = vectorizer.fit_transform(X_train) 
X_test_tfidf = vectorizer.transform(X_test)


# ## Step 5 :  Model Training and Prediction

# ### A. Training

# In[62]:


## Linear SVC
#
classifier = LinearSVC()
classifier.fit(X_train_tfidf, y_train)


# ### B. Prediction

# In[63]:


## Prediction
#
predictions = classifier.predict(X_test_tfidf)


# In[33]:


## Export Results
#
# result_dataframe = pd.DataFrame()
# result_dataframe['Test'] = X_test.tolist()
# result_dataframe['Original'] = labelencoder.inverse_transform(y_test.to_list())
# result_dataframe['Predicted'] = predictions.tolist()
# result_dataframe['Predicted_Label'] = labelencoder.inverse_transform(predictions)

# result_dataframe.to_excel("Result.xlsx")


# ### C. Accuracy

# In[64]:


## Accuracy
#
print(metrics.accuracy_score(y_test, predictions))


# ## Step 7 : Export Model and Requirements

# ### A. Export Classifier, Vectorizer and Encoder

# In[66]:


## Save Classifier, Vectorizer and Encoder
#
with open('type_classifier.pickle', 'wb') as file:
    pickle.dump(classifier, file)

with open('vectorizer.pickle', 'wb') as file:
    pickle.dump(vectorizer, file)

with open('label_encoder.pickle', 'wb') as file:
    pickle.dump(labelencoder, file)


# ## Step 8 : Load Saved Model, Requirment Models and Test it on sample

# In[67]:


test_sample = """All modifications or revisions to submittals and shop drawings must be
clouded, with an appropriate revision number clearly indicated. The
following shall automatically be considered cause for rejection of the
modification or revision whether or not the drawing has been approved
by the Design Professionals:

a. Failure to specifically cloud modifications
b. Unapproved revisions to previous submittals
c. Unapproved departure from Contract Submittals
"""


# In[68]:


## Load Saved Model, Vectorizer and Encoder
#
with open("vectorizer.pickle", 'rb') as file:
    vectorizer_saved = pickle.load(file)

with open("label_encoder.pickle", 'rb') as file:
    encorder_saved = pickle.load(file)

with open("type_classifier.pickle", 'rb') as file:
    classifier_saved = pickle.load(file)


# In[69]:


## Result
#
result_code = classifier_saved.predict(vectorizer_saved.transform([test_sample]))
result_code


# In[72]:


## Result Convert
#
result = encorder_saved.inverse_transform(result_code)
result


# ## Step 9 : Convert Into Python

# In[ ]:


get_ipython().system('jupyter nbconvert --to script "type_classification.ipynb"')


# 
