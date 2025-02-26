# -*- coding: utf-8 -*-
"""sentimental_analysis_amazon_reviews.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1q7evRiI7lf-Fye1kBms0Zmihr74ZgyvK

# Sentiment Analysis of Amazon Reviews

# A. Import Library
"""

import numpy as np
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
from textblob import TextBlob
from wordcloud import WordCloud
import seaborn as sns
import matplotlib.pyplot as plt
import cufflinks as cf
from plotly.offline import init_notebook_mode, iplot
init_notebook_mode(connected = True)
cf.go_offline()
import plotly.graph_objs as go
from plotly.subplots import make_subplots

"""# B. Data Loading"""

#from google.colab import drive
#drive.mount('/content/drive')

df = pd.read_csv("amazon_reviews.csv")
df

df = df.sort_values("total_votes", ascending=False)
df.head()

def missing_values_analysis(df):
    na_columns_ = [col for col in df.columns if df[col].isnull().sum() > 0]
    n_miss = df[na_columns_].isnull().sum().sort_values(ascending=True)
    ratio_ = (df[na_columns_].isnull().sum() / df.shape[0]*100).sort_values(ascending=True)
    missing_df = pd.concat([n_miss, np.around(ratio_, 2)], axis=1, keys=['Missing Values', 'Ratio'])
    missing_df = pd.DataFrame(missing_df)
    return missing_df

def check_dataframe(df, head=5, tail=5):
    print("SHAPE".center(82, '~'))
    print('Rows: {}'.format(df.shape[0]))
    print('Columns: {}'.format(df.shape[1]))
    print("TYPES".center(82,'~'))
    print(df.dtypes)
    print("".center(82, '~'))
    print(missing_values_analysis(df))
    print('DUPLICATED VALUES'.center(82, '~'))
    print(df.duplicated().sum())
    print("QUANTILES".center(82, '~'))

    # Select only numeric columns
    numeric_columns = df.select_dtypes(include=[np.number])
    if not numeric_columns.empty:
        print(numeric_columns.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)
    else:
        print("No numeric columns found.")

check_dataframe(df)

def check_class(dataframe):
    nunique_df = pd.DataFrame({'Variable': dataframe.columns,
                                'Classes': [dataframe[i].nunique()
                                            for i in dataframe.columns]})
    nunique_df = nunique_df.sort_values('Classes', ascending=False)
    nunique_df = nunique_df.reset_index(drop = True)
    return nunique_df

check_class(df)

constraints = ['#B34D22', '#EBE00C', '#1FEB0C', '#0C92EB', '#EB0CD5']
def categorical_variable_summary(df, column_name):
    fig = make_subplots(rows = 1, cols = 2,
                        subplot_titles=('Countplot', 'Percentage'),
                        specs=[[{"type": "xy"}, {'type': 'domain'}]])

    fig.add_trace(go.Bar( y = df[column_name].value_counts().values.tolist(),
                        x = [str(i) for i in df[column_name].value_counts().index],
                        text = df[column_name].value_counts().values.tolist(),
                        textfont = dict(size=14),
                        name = column_name,
                        textposition = 'auto',
                        showlegend = False,
                        marker = dict(color = constraints,
                        line = dict(color = '#DBE6EC', width = 1))),
                row = 1, col = 1)
    fig.add_trace(go.Pie(labels = df[column_name].value_counts().keys(),
                        values = df[column_name].value_counts().values,
                        textfont = dict(size = 18),
                        textposition = 'auto',
                        showlegend = False,
                        name = column_name,
                        marker = dict(colors = constraints)),
                row = 1, col = 2)
    fig.update_layout(title={'text': column_name,
                            'y': 0.9,
                            'x': 0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
                        template = 'plotly_white')
    iplot(fig)
    fig.show()

categorical_variable_summary(df, 'total_votes')

df.review_body.head()

review_example = df.review_body[1031]
review_example

review_example = re.sub("[^a-zA-Z]", '', review_example)
review_example

review_example = review_example.lower().split()
review_example

rt = lambda x: re.sub("[^a-zA-Z]", ' ', str(x))
df["review_body"] = df["review_body"].map(rt)
df["review_body"] = df["review_body"].str.lower()
df.head()

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

df[['polarity', 'subjectivity']] = df['review_body'].apply(lambda Text: pd.Series(TextBlob(Text).sentiment))

for index, row in df.iterrows():
    score = SentimentIntensityAnalyzer().polarity_scores(row['review_body'])
    neg = score['neg']
    neu = score['neu']
    pos = score['pos']
    if neg > pos:
        df.loc[index, 'sentiment'] = "Negative"
    elif pos > neg:
        df.loc[index, 'sentiment'] = "Positive"
    else:
        df.loc[index, 'sentiment'] = "Neutral"

df[df["sentiment"] == "Positive"].sort_values("total_votes", ascending=False).head(5)

categorical_variable_summary(df, 'sentiment')
df

from textblob import TextBlob
import re

def classify_review(review_text):
    # Preprocess review text
    review_text = re.sub("[^a-zA-Z]", ' ', review_text)
    review_text = review_text.lower().split()

    # Calculate polarity score using TextBlob
    polarity_score = TextBlob(' '.join(review_text)).sentiment.polarity

    # Classify sentiment based on polarity score
    if polarity_score > 0:
        return "Positive"
    elif polarity_score < 0:
        return "Negative"
    else:
        return "Neutral"

# Example usage:
new_review = "i got headache after using this product"
feedback = classify_review(new_review)
print("Review sentiment:", feedback)

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import joblib
import re

# Preprocess text data
def preprocess_text(text):
    text = re.sub("[^a-zA-Z]", " ", text)  # Remove non-alphabetic characters
    text = text.lower()  # Convert text to lowercase
    return text

# Load and preprocess dataset (assuming df contains your dataset)
df['clean_text'] = df['review_body']

# Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['clean_text'], df['sentiment'], test_size=0.2, random_state=42)

# Initialize TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer(max_features=5000)

# Fit and transform the training data
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)

# Transform the testing data
X_test_tfidf = tfidf_vectorizer.transform(X_test)

# Initialize SVM classifier
svm_classifier = SVC(kernel='linear')

# Train the classifier
svm_classifier.fit(X_train_tfidf, y_train)

# Save the SVM model
joblib.dump(svm_classifier, "sentiment_model.pkl")

# Save the TF-IDF vectorizer
joblib.dump(tfidf_vectorizer, "tfidf_vectorizer.pkl")

# Evaluate the classifier
y_pred = svm_classifier.predict(X_test_tfidf)
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

# Function to classify new text
def classify_text(new_text):
    cleaned_text = preprocess_text(new_text)
    tfidf_vectorized_text = tfidf_vectorizer.transform([cleaned_text])
    sentiment = svm_classifier.predict(tfidf_vectorized_text)
    return sentiment[0]

# Example usage:
new_review = "my name is afnan"
predicted_sentiment = classify_text(new_review)
print("Predicted sentiment:", predicted_sentiment)

import matplotlib.pyplot as plt
import seaborn as sns

# Function to classify text and visualize sentiment
def classify_and_visualize_text(new_text):
    # Classify the text
    predicted_sentiment = classify_text(new_text)

    # Plot the sentiment along with the input text
    plt.figure(figsize=(8, 6))
    sns.barplot(x=['Positive', 'Negative', 'Neutral'], y=[predicted_sentiment.count('Positive'),
                                                          predicted_sentiment.count('Negative'),
                                                          predicted_sentiment.count('Neutral')])
    plt.title('Predicted Sentiment Distribution')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.show()

    # Print the predicted sentiment
    print("Predicted sentiment:", predicted_sentiment)

# Example usage:
new_review = "I dont't have any complaints, Loved"
classify_and_visualize_text(new_review)

import matplotlib.pyplot as plt
import seaborn as sns

# Visualization of Sentiment Distribution
def plot_sentiment_distribution(data):
    sentiment_counts = data.value_counts()
    plt.figure(figsize=(8, 6))
    sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values)
    plt.title('Sentiment Distribution')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.show()

# Plot sentiment distribution in the dataset
plot_sentiment_distribution(df['sentiment'])

import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns

# Visualization of Confusion Matrix
def plot_confusion_matrix(y_true, y_pred, labels):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.show()


# Plot confusion matrix for model performance evaluation
plot_confusion_matrix(y_test, y_pred, labels=['Positive', 'Negative', 'Neutral'])