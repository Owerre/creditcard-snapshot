# Imports
import pandas as pd

# load the data
df = pd.read_csv('../data/sentence.csv')
# change of name
change = {'RBC VISA': 'RBC Avion Visa Infinite',
          'American Express Blue Cash Preferred ': 'American Express Blue Cash Preferred'}
df.company = df.company.replace(change)


def overall_sentiment_func(data, threshold=None):
    """
    This function returns the total number of positive,
    negative, and neutral  sentiment for each credit card
    """
    df = pd.DataFrame()  # Initialize dataframe
    cards = list(data.company.unique())  # List of all credit cards
    for card in cards:
        # positive sentiments
        pos_senti = data[data.sentiment > threshold]
        # neutral sentiments
        neu_senti = data[data.sentiment == threshold]
        # negative sentiments
        neg_senti = data[data.sentiment < threshold]
        # positives sentiment count for each card
        pos_count = pos_senti[pos_senti.company == card]['sentiment'].count()
        # neutral sentiment count for each card
        neu_count = neu_senti[neu_senti.company == card]['sentiment'].count()
        # negatives sentiment count for each card
        neg_count = neg_senti[neg_senti.company == card]['sentiment'].count()
        # dictionary to hold the count of positive, negative, and neutral sentences for a card
        total_dict = dict()
        total_dict['Overall'] = [pos_count, neg_count, neu_count]
        task_dict = {'sentiment': ['Positive', 'Negative', 'Neutral']}
        # join dictionary so that  task_dict appears first
        topic_dict = {**task_dict, **total_dict}
        df = df.append({'overall_sentiment': topic_dict}, ignore_index=True)
    return df

#print(overall_sentiment_func(df, threshold=0).head())
result = overall_sentiment_func(df, threshold=0)
# load the composite dataframe
topic_df = pd.read_csv('../data/creditcard_data.csv')
# add the overall sentiment as a column
topic_df['overall'] = result['overall_sentiment']

# Review count
review_count = df.groupby(
    'company')['sentiment'].count().sort_values(ascending=False)

# Add total number of review for each credit card
topic_df['num_reviews'] = topic_df.creditcard
topic_df['num_reviews'] = topic_df['num_reviews'].map(dict(review_count))

# Save data as csv file
topic_df.to_csv('../data/creditcard_data.csv', index=False)
