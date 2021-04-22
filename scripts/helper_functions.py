# Created by Solomon Owerre.
import re
import nltk
import gensim
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import sent_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from collections import Counter
from gensim import corpora, models
from gensim.models.wrappers import LdaMallet
from gensim.models import CoherenceModel, LdaModel, LdaMulticore
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from gensim.models.word2vec import Word2Vec
from nltk.stem import WordNetLemmatizer, PorterStemmer
# Model performance metrics
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, auc, recall_score
from sklearn.metrics import roc_curve, roc_auc_score, average_precision_score, precision_recall_curve

mallet_path = "/Users/sowerre/mallet-2.0.8/bin/mallet"


def review_to_sent(data, review, company):
    """Converts reviews to sentences and keeps track of company name for each sentence"""
    sentence_tokens = [[sentence for sentence in sent_tokenize(
        data[review].loc[i])] for i in range(len(data))]
    count_sentences = [len(x) for x in sentence_tokens]
    sentences = [
        sentence for sub_sentence in sentence_tokens for sentence in sub_sentence]
    count_company = [[x] for x in data[company]]
    company_token = []
    for idx, val in enumerate(count_sentences):
        company_token.append(count_company[idx] * val)
    company_names = [name for names in company_token for name in names]
    return sentences, company_names


def print_review(data, index=None):
    """Display index row of the review dataframe"""
    text = data[data.index == index].values.reshape(3)
    review = text[0]
    rating = text[1]
    company = text[2]
    print('Review:', review)
    print('Rating:', rating)
    print('Credit card:', company)


def print_sentence(data, index=None):
    """Display index row of the sentence dataframe"""
    text = data[data.index == index].values.reshape(4)
    sentence = text[0]
    company = text[1]
    sentiment = text[2]
    positivity = text[3]
    print('Sentence:', sentence)
    print('Credit card:', company)
    print('Sentiment:', sentiment)
    print('Positivity:', positivity)


def pre_process_text(data, text_string):
    """clean the review texts"""
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


def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)


def word_lemmatizer(text):
    """Word lemmatization function"""
    lemmatizer = WordNetLemmatizer()
    text = lemmatizer.lemmatize(text, get_wordnet_pos(text))
    return text


# By inspection, I will add more stopwords to the default nltk stopwords
my_stop_words = ['capital', 'america', 'redcard', 'target', 'amazon', 'card', 'credit', 'merrick', 'discover', 'citi',
                 'amex', 'express', 'go', 'paypal', 'chase', 'american', 'one', 'would', 'ask', 'really',
                 'get', 'know', 'express', 'ever', 'use', 'say', 'recently', 'also', 'always', 'give',  'tell',
                 'take', 'never', 'costco', 'time', 'make', 'try', 'number', 'send', 'new', 'even',
                 'sony', 'us', 'husband', 'car', 'capitol', 'wife', 'book', 'could', 'okay', 'mastercard', 'want',
                 'honestly', 'eppicard', 'need', 'family', 'cap', 'another', 'line', 'com', 'fico', 'quicksilver',
                 'link', 'sear', 'pay', 'may', 'company', 'bank', 'call', 'account', 'receive', 'told', 'day', 'well',
                 'think', 'look', 'sure', 'easy', 'money', 'people', 'business', 'review', 'something', 'come', 'away']

stop_words = stopwords.words('english')
stop_words.extend(my_stop_words)


def my_tokenizer(text):
    """Tokenize review text"""
    text = text.lower()  # lower case
    text = re.sub("\d+", " ", text)  # remove digits
    tokenizer = RegexpTokenizer(r'\w+')
    token = [word for word in tokenizer.tokenize(text) if len(word) > 2]
    token = [word_lemmatizer(x) for x in token]
    token = [s for s in token if s not in stop_words]
    return token


def detokenizer(text):
    """Remove wide space in review texts"""
    my_detokenizer = TreebankWordDetokenizer().detokenize(sent_tokenize(text))
    return my_detokenizer


def topic_threshold(doc_topic, topic_vector, threshold=None):
    """Return the topic number if the topic is more than 70% dominant"""
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


def compute_coherence_lda(corpus, dictionary, start=None, limit=None, step=None):
    """Compute c_v coherence for various number of topics """
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


def add_bigram(token_list):
    """add bigrams in the data"""
    bigram = gensim.models.Phrases(token_list)
    bigram = [bigram[line] for line in token_list]
    return bigram


def add_trigram(token_list):
    """add trigrams in the data"""
    bigram = add_bigram(token_list)
    trigram = gensim.models.Phrases(bigram)
    trigram = [trigram[line] for line in bigram]
    return trigram


def doc_term_matrix(data, text):
    """Returns document-term matrix, vocabulary, and word_id"""
    counter = CountVectorizer(tokenizer=my_tokenizer, ngram_range=(1, 1))
    data_vectorized = counter.fit_transform(data[text])
    X = data_vectorized.toarray()
    bow_docs = pd.DataFrame(X, columns=counter.get_feature_names())
    vocab = tuple(bow_docs.columns)
    word2id = dict((v, idx) for idx, v in enumerate(vocab))
    return data_vectorized, vocab, word2id, counter


def word2vec_embedding(list_of_tokens):
    """Train word2vec on the corpus"""
    num_features = 300
    min_word_count = 1
    num_workers = 2
    window_size = 6
    subsampling = 1e-3

    model = Word2Vec(list_of_tokens, workers=num_workers,
                     size=num_features, min_count=min_word_count,
                     window=window_size, sample=subsampling)
    return model


def credit_card(data):
    """Returns topics, topic_sentiments, and credit cards"""
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


def Plot_ROC_Curve_and_PRC_Cross_Val(model, n_training_samples, n_training_labels, color=None, label=None):
    """ Plot of ROC and PR Curves for the cross-validation training set"""
    model.fit(n_training_samples, n_training_labels)

    y_pred_proba = cross_val_predict(model, n_training_samples, n_training_labels, cv=5,
                                     method="predict_proba")

    # Compute the fpr and tpr for each classifier
    fpr, tpr, thresholds = roc_curve(n_training_labels, y_pred_proba[:, 1])

    # Compute the precisions and recalls for the classifier
    precisions, recalls, thresholds = precision_recall_curve(
        n_training_labels, y_pred_proba[:, 1])

    # Compute the area under the ROC curve for each classifier
    area_auc = roc_auc_score(n_training_labels, y_pred_proba[:, 1])

    # Compute the area under the PR curve for the classifier
    area_prc = auc(recalls, precisions)

    # ROC Curve
    plt.subplot(121)
    plt.plot(fpr, tpr, color=color, label=(label) % area_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.axis([0, 1, 0, 1])
    plt.xlabel('False positive rate (FPR)')
    plt.ylabel('True positive rate (TPR)')
    plt.title('ROC Curve on CV set')
    plt.legend(loc='best')

    # PR Curve
    plt.subplot(122)
    plt.plot(recalls, precisions, color=color, label=(label) % area_prc)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve on CV set')
    plt.legend(loc='best')


def Test_Prediction(model, n_training_samples, n_training_labels, n_test_samples, n_test_labels):
    """ This function returns prediction on the test set """
    # Fit the training set
    model.fit(n_training_samples, n_training_labels)

    # Make prediction on the test set
    y_predict = model.predict(n_test_samples)

    # Compute the accuracy of the model
    accuracy = accuracy_score(n_test_labels, y_predict)

    # Predict probability
    y_predict_proba = model.predict_proba(n_test_samples)[:, 1]

    print(
        '****************************************************************************')
    print('Test accuracy:  %f' % (accuracy))
    print('AUROC: %f' % (roc_auc_score(n_test_labels, y_predict_proba)))
    print('AUPRC: %f' %
          (average_precision_score(n_test_labels, y_predict_proba)))
    print('Predicted classes:', np.unique(y_predict))
    print('Confusion matrix:\n', confusion_matrix(n_test_labels, y_predict))
    print('Classification report:\n',
          classification_report(n_test_labels, y_predict))
    print(
        '****************************************************************************')


def Plot_ROC_Curve_and_PRC(model, n_training_samples, n_training_labels, n_test_samples, n_test_labels,
                           color=None, label=None):
    """ Plot of ROC and PR Curves for the test set"""

    # fit the model
    model.fit(n_training_samples, n_training_labels)

    # Predict probability
    y_pred_proba = model.predict_proba(n_test_samples)[:, 1]

    # Compute the fpr and tpr for each classifier
    fpr, tpr, thresholds = roc_curve(n_test_labels, y_pred_proba)

    # Compute the precisions and recalls for the classifier
    precisions, recalls, thresholds = precision_recall_curve(
        n_test_labels, y_pred_proba)

    # Compute the area under the ROC curve for each classifier
    area_auc = roc_auc_score(n_test_labels, y_pred_proba)

    # Compute the area under the PR curve for the classifier
    area_prc = auc(recalls, precisions)

    # ROC Curve
    plt.subplot(121)
    plt.plot(fpr, tpr, color=color, label=(label) % area_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.axis([0, 1, 0, 1])
    plt.xlabel('False positive rate (FPR)')
    plt.ylabel('True positive rate (TPR)')
    plt.title('ROC Curve on test set')
    plt.legend(loc='best')

    # PR Curve
    plt.subplot(122)
    plt.plot(recalls, precisions, color=color, label=(label) % area_prc)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve on test set')
    plt.legend(loc='best')
