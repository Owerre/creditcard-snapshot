####################################
# Author: S. A. Owerre
# Date modified: 03/07/2021
# Class: Text Analytics
####################################

# Filter warnings
import warnings
warnings.filterwarnings("ignore")

# Text analytics
import re
import nltk
import gensim
from collections import Counter
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from gensim import corpora, models
from nltk.tokenize import sent_tokenize
from nltk.tokenize import RegexpTokenizer
from gensim.models.word2vec import Word2Vec
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize.treebank import TreebankWordDetokenizer
from gensim.models import CoherenceModel, LdaModel, LdaMulticore
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# Sentiment analysis
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class TextAnalytics:
    """
    Class for processing text data
    """
    def __init__(self):
        """
        Parameter initialization
        """
        
    def review_to_sent(self, data, review, company):
        """
        Converts reviews to sentences and keeps track 
        of company name for each sentence
        
        Parameter
        --------
        data: Pandas DataFrame
        reviews: Text column for reviews
        company: Name of credit card compnay
        
        Returns
        -------
        Sentences in each review, and company names
        """
        sentence_tokens = [[sentence for sentence in sent_tokenize(
            data[review].loc[i])] for i in range(len(data))]
        count_sentences = [len(x) for x in sentence_tokens]
        sentences = [sentence for sub_sentence in sentence_tokens for sentence in sub_sentence]
        count_company = [[x] for x in data[company]]
        
        company_token = []
        for idx, val in enumerate(count_sentences):
            company_token.append(count_company[idx] * val)
        company_names = [name for names in company_token for name in names]
        return sentences, company_names

    def print_review(self, data, index=None):
        """
        Display index row of the review dataframe
        
        Parameter
        --------
        data: Pandas DataFrame
    
        Returns
        -------
        Print out review, rating, and credit card company
        """
        text = data[data.index == index].values.reshape(3)
        review = text[0]
        rating = text[1]
        company = text[2]
        print('Review:', review)
        print('Rating:', rating)
        print('Credit card:', company)

    def print_sentence(self, data, index=None):
        """
        Display index row of the sentence dataframe
        
        Parameter
        --------
        data: Pandas DataFrame
    
        Returns
        -------
        Print out sentence, sentiment, and positivity
        """
        text = data[data.index == index].values.reshape(4)
        sentence = text[0]
        company = text[1]
        sentiment = text[2]
        positivity = text[3]
        print('Sentence:', sentence)
        print('Credit card:', company)
        print('Sentiment:', sentiment)
        print('Positivity:', positivity)

    def pre_process_text(self, data, text_string):
        """
        Clean the review texts
        
        Parameter
        --------
        data: Pandas DataFrame
        text_string: Text column
    
        Returns
        -------
        Pre-processed data
        """
        data[text_string] = data[text_string].str.replace(r"http\S+", "")
        data[text_string] = data[text_string].str.replace(r"http", "")
        data[text_string] = data[text_string].str.replace(r"@\S+", "")
        data[text_string] = data[text_string].str.replace(
            r"[^A-Za-z0-9(),!?@\'\`\"\_\n]", " ")
        data[text_string] = data[text_string].str.replace(r"@", "at")
        data[text_string] = data[text_string].str.replace(r"\n", "")
        data[text_string] = data[text_string].str.replace(r"\t", "")
        data[text_string] = data[text_string].str.replace(r"\d+", "")
        data[text_string] = data[text_string].str.lower()
        return data

    def get_wordnet_pos(self, word):
        """
        Map POS tag to first character lemmatizer() accepts
        """
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}

        return tag_dict.get(tag, wordnet.NOUN)

    def word_lemmatizer(self, text):
        """
        Word lemmatization function
        
        Parameter
        --------
        text: text
    
        Returns
        -------
        Lemmatized text
        """
        lemmatizer = WordNetLemmatizer()
        text = lemmatizer.lemmatize(text, self.get_wordnet_pos(text))
        return text

    def my_tokenizer(self, text):
        """
        Tokenize review text
        
        Parameter
        --------
        text: text
    
        Returns
        -------
        Tokenized words
        """
        # By inspection, I will add more stopwords to the default nltk stopwords
        my_stop_words = ['capital', 'america', 'redcard', 'target', 'amazon',
         'card', 'credit', 'merrick', 'discover', 
         'citi','amex', 'express', 'go', 'paypal', 'chase', 
         'american', 'one', 'would', 'ask', 'really',
        'get', 'know', 'express', 'ever', 'use', 'say', 
         'recently', 'also', 'always', 'give',  'tell',
        'take', 'never', 'costco', 'time', 'make', 'try', 
         'number', 'send', 'new', 'even',  'come', 'away'
         'sony', 'us', 'husband', 'car', 'capitol', 'wife', 
         'book', 'could', 'okay', 'mastercard', 'want',
        'honestly', 'eppicard', 'need', 'family', 'cap',
        'another', 'line', 'com', 'fico', 'quicksilver',
         'link', 'sear', 'pay', 'may', 'company', 'bank', 
         'account', 'receive', 'told', 'day','call',                    
         'well','think', 'look', 'sure', 'easy', 'money', 
         'people', 'business', 'review', 'something'
                        ]
        stop_words = stopwords.words('english')
        stop_words.extend(my_stop_words)
        text = text.lower()  # lower case
        text = re.sub("\d+", " ", text)  # remove digits
        tokenizer = RegexpTokenizer(r'\w+')
        token = [word for word in tokenizer.tokenize(text) if len(word) > 2]
        token = [self.word_lemmatizer(x) for x in token]
        token = [s for s in token if s not in stop_words]
        return token

    def detokenizer(self, text):
        """
        Remove wide space in review texts
        
        Parameter
        --------
        text: sentence
    
        Returns
        -------
        Preprocessed text
        """
        detokenizer = TreebankWordDetokenizer()
        my_detokenizer = detokenizer.detokenize(sent_tokenize(text))
        return my_detokenizer

    def vader_polarity_scores(self, sentence):
        """
        Compound polarity score of each senetence
        in vader sentiment analysis
        
        Parameter
        --------
        sentence: sentence
        
        Returns
        -------
        Compound polarity score
        """
        sia = SentimentIntensityAnalyzer()
        score = sia.polarity_scores(sentence)
        return score['compound']
    
    def blob_polarity_scores(self, sentence):
        """
        Polarity score of each senetence
        in textblob sentiment analysis
        
        Parameter
        --------
        sentence: sentence
        
        Returns
        -------
        Polarity score
        """ 
        score = TextBlob(sentence).sentiment.polarity
        return score

    def topic_threshold(self, doc_topic, topic_vector, threshold=None):
        """
        Return the topic number if the topic is more than threshold
        
        Parameter
        --------
        doc_topic: Document-topic matrix (Pandas DataFrame)
        topic_vector: Topic vector (Pandas DataFrame)
        threshold: threshold
        
        Returns
        -------
        Topic number if the topic is more than threshold
        """
        topic_num_list = []
        for i in range(len(topic_vector)):
            topic_num = [idx for idx, value in enumerate(
                doc_topic[i]) if value > threshold]
            if topic_num != []:
                topic_num = topic_num[0]
            else:
                topic_num = 'None'
            topic_num_list.append(topic_num)
        return topic_num_list

    def add_bigram(tself, token_list):
        """
        Add bigrams in the data
            
        Parameter
        --------
        token_list: list of tokens
    
        Returns
        -------
        Bigram list
        """
        bigram = gensim.models.Phrases(token_list)
        bigram = [bigram[line] for line in token_list]
        return bigram

    def add_trigram(self, token_list):
        """
        Add trigrams in the data
        
        Parameter
        --------
        token_list: list of tokens
    
        Returns
        -------
        Trigram list
        """
        bigram = self.add_bigram(token_list)
        trigram = gensim.models.Phrases(bigram)
        trigram = [trigram[line] for line in bigram]
        return trigram

    def doc_term_matrix(self, data, text):
        """
        Returns document-term matrix
        
        Parameter
        --------
        data: Pandas DataFrame
        text: text column
    
        Returns
        -------
        Bag of words dataframe, vocab, model
        """
        counter = CountVectorizer(tokenizer=self.my_tokenizer, ngram_range=(1, 1))
        data_vectorized = counter.fit_transform(data[text])
        X = data_vectorized.toarray()
        bow_docs = pd.DataFrame(X, columns=counter.get_feature_names())
        vocab = tuple(bow_docs.columns)
        word2id = dict((v, idx) for idx, v in enumerate(vocab))
        return data_vectorized, vocab, word2id, counter

    def word2vec_embedding(self, list_of_tokens):
        """
        Train word2vec on the corpus
        
        Parameter
        --------
        list_of_tokens: list of tokens
    
        Returns
        -------
        Trained word2vec model
        """
        num_features = 300
        min_word_count = 1
        num_workers = 2
        window_size = 6
        subsampling = 1e-3

        model = Word2Vec(sentences=list_of_tokens, workers=num_workers,
                         vector_size=num_features, min_count=min_word_count,
                        window=window_size, sample=subsampling)
        return model

    def credit_card(self, data):
        """
        Returns topics, topic_sentiments, and credit cards
        
        Parameter
        --------
        data: Pandas DataFrame
    
        Returns
        -------
        Topics and topic sentence
        """
        topic_list = data.topics.unique()
        card_lists = []
        topic_sentiment = []
        topics = []
        for i in range(len(topic_list)):
            specific = df[df.topics == topic_list[i]][[
                'topics', 'creditcards', 'sentiments']].reset_index(drop=True)
            group_table = specific.groupby('creditcards')[
                'sentiments'].mean().sort_values(ascending=False)
            card_lists.append(list(group_table.index))
            topic_sentiment.append(group_table.values.round(2))
            for j in range(len(group_table)):
                topics.append(topic_list[i])

        # Convert the list of lists to list
        card_list = [card for sub_card in card_lists for card in sub_card]
        topic_sen = [sen for sub_sen in topic_sentiment for sen in sub_sen]
        return topics, card_list, topic_sen
    
     def compute_coherence_lda(self, corpus, dictionary, start=None, limit=None, step=None):
        """
        Compute c_v coherence for various number of topics
        """
        topic_coherence = []
        model_list = []
        tokens_list = df.trigram_tokens.values.tolist()
        texts = [[token for sub_token in tokens_list for token in sub_token]]
        for num_topics in range(start, limit, step):
            model = LdaMulticore(corpus=corpus, id2word=dictionary, num_topics=num_topics,
                                 eta='auto', workers=4, passes=20, iterations=100,
                                 random_state=42, eval_every=None,
                                 alpha='asymmetric',  # shown to be better than symmetric in most cases
                                 decay=0.5, offset=64  # best params from Hoffman paper
                                 )
            model_list.append(model)
            coherencemodel = CoherenceModel(
                model=model, texts=texts, dictionary=dictionary, coherence='c_v')
            topic_coherence.append(coherencemodel.get_coherence())
        return model_list, topic_coherence
    
   