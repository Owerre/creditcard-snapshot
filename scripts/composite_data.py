# Imports
import pandas as pd

# load the data
df = pd.read_csv('../data/creditcard_topics.csv')

# change of name
change = {'RBC VISA': 'RBC Avion Visa Infinite',
          'American Express Blue Cash Preferred ': 'American Express Blue Cash Preferred'}
df.creditcards = df.creditcards.replace(change)

# Drop these topics: Bill Disputes and Fraud Issues
df = df[(df.topics != 'Bill Disputes') & (df.topics != 'Fraud Issues')]
# print(df.sentiment.head())


def webapp_data(data, threshold=None):
    """This function filters all the results in a dataframe to be used in a web app"""
    df = pd.DataFrame()  # Initialize dataframe
    cards = list(data.creditcards.unique())  # List of all credit cards
    for card in cards:
        data = data[['topics', 'creditcards',
                     'sentences', 'sentiments']]
        df_sent = data[data.creditcards ==
                       card]['sentences'].reset_index(drop=True)
        # 3 positive and 3 negative sentences for each card
        sent = df_sent.loc[0] + 'varsep' + df_sent.loc[1] + 'varsep' + df_sent.loc[2] + 'varsep' + df_sent.loc[len(
            df_sent) - 1] + 'varsep' + df_sent.loc[len(df_sent) - 2] + 'varsep' + df_sent.loc[len(df_sent) - 3]
        # positive topics for sentiment greater than threshold
        pos_topic = data[data.sentiments > threshold]
        # neutral topics for sentiment equal to threshold
        neu_topic = data[data.sentiments == threshold]
        # negative topics for sentiment greater than threshold
        neg_topic = data[data.sentiments < threshold]
        pos_topic = pos_topic[pos_topic.creditcards == card].reset_index(
            drop=True)  # positives for each card
        neu_topic = neu_topic[neu_topic.creditcards == card].reset_index(
            drop=True)  # neutral for each card
        neg_topic = neg_topic[neg_topic.creditcards == card].reset_index(
            drop=True)  # negatives for each card
        # No of positive sentences under a topic
        pos_dict = dict(pos_topic.groupby('topics')['sentiments'].count())
        # No of neutral sentences under a topic
        neu_dict = dict(neu_topic.groupby('topics')['sentiments'].count())
        # No of negative sentences under a topic
        neg_dict = dict(neg_topic.groupby('topics')['sentiments'].count())
        # dictionary to hold the number of positive and negative sentences under a topic
        total_dict = dict()
        for pos, neg, neu in zip(pos_dict.items(), neg_dict.items(), neu_dict.items()):
            total_dict[pos[0]] = [pos[1], neg[1], neu[1]]
        # for google bar chart display
        task_dict = {'Task': ['Satisfied', 'Unsatisfied', 'Neutral']}
        # sort total_dict
        sorted_total_dict = dict(
            sorted(total_dict.items(), key=lambda kv: kv[1], reverse=True))
        # join dictionary so that  task_dict appears first
        topic_dict = {**task_dict, **sorted_total_dict}
        df = df.append({'creditcard': card, 'topic': topic_dict,
                        'pos_neg_sentence': sent}, ignore_index=True)
    return df


# Extract the data from the function
data = webapp_data(df, threshold=0.0)
# print data
print(data.head())

# Save data as csv file
data.to_csv('../data/creditcard_data.csv', index=False)
