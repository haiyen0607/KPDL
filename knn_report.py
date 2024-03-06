# -*- coding: utf-8 -*-
"""KNN_report.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1boKompdXBFgSBLj-zx_kUi73w2Ad4y0e
"""

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/MyDrive/project

# Commented out IPython magic to ensure Python compatibility.
# %pip install pyvi

# System library
import os
import time
import pickle
import warnings

# Statistics library
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt

# Natural Language Toolkit
import nltk
import gensim
from pyvi import ViUtils, ViTokenizer

# Machine Learning
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier
from sklearn.decomposition import TruncatedSVD
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB, CategoricalNB
from sklearn.ensemble import RandomForestClassifier, VotingClassifier

from sklearn.metrics import accuracy_score, classification_report

# utils methods
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator, TransformerMixin

# Preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from imblearn import (
    over_sampling as ios,
    under_sampling as ius,
    pipeline as ipl
)

SEED = 42
RANDOM_STATE=123
warnings.filterwarnings('ignore')
sns.set(rc = {'figure.figsize':(15, 10)})
np.random.seed(SEED)

DATA_PATH = 'data/'
MODEL_PATH = 'model/'

# read dantri.json file
dantri = pd.read_json(os.path.join(DATA_PATH, 'dantri.json'))

# read vietnamese stopwords
with open(os.path.join(DATA_PATH, 'vietnamese-stopwords.txt'), 'r') as f:
  stopwords = [line.rstrip("\n").strip().replace(' ', '_') for line in f]

# remove `Nhân ái` class
dantri = dantri[dantri['category'] != 'Nhân ái']

dantri.isna().sum()

data = dantri[['content', 'category']]

count = data["category"].value_counts()
num_of_post_each_topic = pd.DataFrame(
    {"category": count.index, "count": count.values}
)
num_of_post_each_topic

def create_bar_plot(df=None, title="Số lượng bài báo trên từng hạng mục", y_arrow=500):
  fig = px.histogram(
    df,
    x='category',
    y='count',
    color='category',
    title=title,
    color_discrete_sequence=px.colors.qualitative.Light24,
    opacity=0.75
  )
  fig.update_yaxes(showgrid=True)  # the y-axis is in dollars
  fig.update_layout(  # customize font and legend orientation & position
      font_family="Arial",
      legend=dict(
          title=None, orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
      ),
      yaxis_title="Số lượng bài báo",
      xaxis_title="Hạng mục",
  )


  fig.add_shape(  # add a horizontal "target" line
      type="line",
      line_color="#16FF32",
      line_width=3,
      opacity=1,
      line_dash="dot",
      x0=0,
      x1=1,
      xref="paper",
      y0=929,
      y1=929,
      yref="y",
  )

  fig.add_annotation(  # add a text callout with arrow
      text="Số lượng ít nhất", x="Pháp luật", y=y_arrow, arrowhead=1, showarrow=True
  )


  fig.show()

categories = data['category'].unique()
categories

data['len'] = data['content'].str.len()
data.head()

def truncate_data(df, category):
  df_category = df.query(f"`category` == '{category}'")
  describe = df_category['len'].describe()
  at_75th = int(describe['75%'])
  at_25th = int(describe['25%'])
  return df_category[(df_category['len'] <= (at_75th-at_25th) * 3)]

data_dict = {}
for category in categories:
  data_dict[category] = truncate_data(data, category)

newdata = pd.DataFrame(columns=['content', 'category', 'len'])
newdata

for key, value in data_dict.items():
  newdata = newdata.append(value)

newdata.reset_index(drop=True, inplace=True)

class TextCleaner(BaseEstimator, TransformerMixin):
    def __init__(self) -> None:
        super().__init__()

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        cleaned_texts = []
        for text in X:
            cleaned_text = self.clean_text(text)
            cleaned_texts.append(cleaned_text)
        return np.array(cleaned_texts)

    @staticmethod
    def clean_text(content: str):
        # Text Normalizer
        # lowercase content
        # content = content.lower()
        # # remove white space
        # content = " ".join([x for x in content.split()])
        # # remove punctuation and digits
        # content = content.translate(str.maketrans("", "", punc_custom)).translate(
        #     str.maketrans("", "", digits)
        # )

        # Sử dụng `gensim` để xử lý cơ bản text
        tokens = gensim.utils.simple_preprocess(content)
        content = " ".join(tokens)
        # tokenize content
        content = ViTokenizer.tokenize(content)

        return content

X, label = newdata['content'].values, newdata['category'].values

print(X.shape, label.shape)

le = LabelEncoder()
y = le.fit_transform(label)

print(le.classes_)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=RANDOM_STATE)

train_category = pd.DataFrame({'category': y_train})
train_category.head()

count = train_category["category"].value_counts()
num_of_post_each_topic = pd.DataFrame(
    {"category_le": count.index, "count": count.values}
)
num_of_post_each_topic['category'] = le.inverse_transform(num_of_post_each_topic['category_le'])
num_of_post_each_topic.head()

num_of_post_each_topic['count'].describe()

# No Cleaner
# count_vectorizer_no_cleaner = CountVectorizer(stop_words=stopwords)
# count_vectorizer_no_cleaner.fit(X_train)
# MAX_FEATURES = len(count_vectorizer_no_cleaner.vocabulary_)

# With Cleaner
# text_cleaner = TextCleaner()
# count_vectorizer_with_cleaner = CountVectorizer(stop_words=stopwords)
# X_train_with_cleaner = text_cleaner.fit_transform(X_train)
# count_vectorizer_with_cleaner.fit(X_train_with_cleaner)
# MAX_FEATURES_WITH_CLEANER = len(count_vectorizer_with_cleaner.vocabulary_)

# MAX_FEATURES_WITH_CLEANER #, MAX_FEATURES

# MAX_FEATURES_WITH_CLEANER = 30000
def create_pipeline(stop_words, cleaner=False, max_features=10000, reduction=False, n_components=5000):
  steps = []

  count_vectorizer = CountVectorizer(stop_words=stop_words, max_features=max_features)
  if cleaner:
    text_cleaner = TextCleaner()
    steps.append(('cleaner', text_cleaner))

  # Add steps to convert text to matrix
  steps.append(('count_vectorizer', count_vectorizer))
  steps.append(('tfidf_transformer', TfidfTransformer()))

  if reduction:
    steps.append(('reduction', TruncatedSVD(n_components=n_components)))

  return Pipeline(steps)

MAX_FEATURES = 20000
N_COMPONENTS = 5000

pipeline = {}
# pipeline['only_cleaner'] = create_pipeline(stopwords, cleaner=True, max_features=MAX_FEATURES)
pipeline['cleaner_and_reduction'] = create_pipeline(stopwords, cleaner=True, max_features=MAX_FEATURES, reduction=True, n_components=N_COMPONENTS)

# transform train and test set
# X_train_cleaner_ = pipeline['only_cleaner'].fit_transform(X_train)
# X_test_cleaner_ = pipeline['only_cleaner'].transform(X_test)

X_train_cleaner_and_reduction_ = pipeline['cleaner_and_reduction'].fit_transform(X_train)
X_test_cleaner_and_reduction_ = pipeline['cleaner_and_reduction'].transform(X_test)

# Save processed data
with open(os.path.join(MODEL_PATH, 'X_train_cleaner_and_reduction_.pkl'), 'wb') as f:
  pickle.dump(X_train_cleaner_and_reduction_, f)

with open(os.path.join(MODEL_PATH, 'X_test_cleaner_and_reduction_.pkl'), 'wb') as f:
  pickle.dump(X_test_cleaner_and_reduction_, f)

sampling = {}
categories_geq_600 = num_of_post_each_topic[num_of_post_each_topic['count'] >= 600][['category_le', 'count']]
categories_le_600 = num_of_post_each_topic[num_of_post_each_topic['count'] < 600][['category_le', 'count']]
# num_of_post_each_topic['count'] >= 700
# categories_geq_700
sampling['under'] = {
    key: 600
    for (key, value) in categories_geq_600.values
  }
sampling['over'] = {key: 600 for (key, value) in categories_le_600.values}
sampling



# over = ios.BorderlineSMOTE(sampling_strategy=sampling['over'], n_jobs=-1)
# under = ius.RandomUnderSampler(sampling_strategy=sampling['under'])

# sampling_steps = [('over', over), ('under', under)]
# sampling_pipeline = ipl.Pipeline(sampling_steps)

# X_train_cleaner_sampled_, y_train_cleaner_sampled_ = sampling_pipeline.fit_resample(X_train_cleaner_, y_train)

over = ios.BorderlineSMOTE(sampling_strategy=sampling['over'], n_jobs=-1)
under = ius.RandomUnderSampler(sampling_strategy=sampling['under'])

sampling_steps = [('over', over), ('under', under)]
sampling_pipeline = ipl.Pipeline(sampling_steps)

X_train_cleaner_and_reduction_sampled_, y_train_cleaner_and_reduction_sampled_ = sampling_pipeline.fit_resample(X_train_cleaner_and_reduction_, y_train)

from collections import Counter
Counter(y_train_cleaner_and_reduction_sampled_)

def evaluation_model(y_pred, y_test):
  acc = accuracy_score(y_test, y_pred)
  print("- Acc = {}".format(acc))
  print(classification_report(y_test, y_pred, target_names=le.classes_))
  return acc

import numpy as np

class KNNClassifier:
    def __init__(self, k):
        self.k = k

    def fit(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train

    def predict(self, X_test):
        y_pred = []
        for test_point in X_test:
            distances = []
            for train_point in self.X_train:
                distance = self.euclidean_distance(test_point, train_point)
                distances.append(distance)
            sorted_indices = np.argsort(distances)
            nearest_indices = sorted_indices[:self.k]
            nearest_labels = [self.y_train[i] for i in nearest_indices]
            prediction = self.majority_vote(nearest_labels)
            y_pred.append(prediction)
        return y_pred

    def euclidean_distance(self, x1, x2):
        return np.sqrt(np.sum((x1 - x2) ** 2))

    def majority_vote(self, labels):
        unique, counts = np.unique(labels, return_counts=True)
        return unique[np.argmax(counts)]

def accuracy_score(y_true, y_pred):
    return np.mean(y_true == y_pred)

from sklearn.metrics import classification_report
def custom_classification_report(y_true, y_pred, target_names):
    # Calculate precision, recall, and f1-score for each class
    report = classification_report(y_true, y_pred, target_names=target_names, output_dict=True)

    # Print the header
    header = "{:<20} {:<20} {:<20} {:<20} {:<20}".format("Class", "Precision", "Recall", "F1-Score", "Support")
    print(header)
    print("-" * len(header))

    # Print scores for each class
    for class_name in target_names:
        precision = report[class_name]['precision']
        recall = report[class_name]['recall']
        f1_score = report[class_name]['f1-score']
        support = report[class_name]['support']

        class_line = "{:<20} {:<20.2f} {:<20.2f} {:<20.2f} {:<20}".format(class_name, precision, recall, f1_score, support)
        print(class_line)

# Initialize and train KNN model
knn = KNNClassifier(k=3)
knn.fit(X_train_cleaner_and_reduction_sampled_, y_train_cleaner_and_reduction_sampled_)

# Make predictions
y_pred = knn.predict(X_test_cleaner_and_reduction_)

# Evaluate model
print("Accuracy:", accuracy_score(y_test, y_pred))
# Print custom classification report
custom_classification_report(y_test, y_pred, le.classes_)

