# Created by Solomon Owerre.

import numpy as np
import ast
import pandas as pd
from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from wtforms import Form, SelectField

app = Flask('__name__')
# Load data
data = pd.read_csv('data/creditcard_data.csv')
data.index = data.creditcard


def get_data(data, index):
    """Extract data for a specific credit card"""
    data = data.loc[index]
    data = list(data)
    return data


class CreditCardForm(Form):
    features = [
        'Citi Double Cash Card',
        'Capital One Venture Rewards',
        'Capital One Quicksilver Rewards',
        'TD Cash Visa Credit Card', 'Discover it Secured',
        'American Express Business Gold Rewards Credit Card',
        'Discover it Cash Back', 'BMO MASTERCARD', 'Discover it Miles',
        'RBC Avion Visa Infinite',
        'American Express Blue Cash Preferred',
        'Bank of America Travel Rewards Credit Card',
        'Bank of America Cash Rewards Credit Card',
        'TD First Class Travel VISA Infinite Card',
        'Citi Platinum World Elite', 'Citi Simplicity Card',
        'American Express Platinum Card', 'Citi Diamond Preferred Card',
        'Chase Sapphire Preffered Card', 'Aspire Visa',
        'Chase Freedom Unlimited',
        'Capital One Secured Credit Card', 'Credit One Bank',
        'Costco Anywhere Visa Card by Citi', 'Chase Amazon Reward Visa',
        'Capital One Platinum Costco MASTERCARD', 'Capital One Platinum',
        'Canadian Tire MASTERCARD', 'Barclays Bank',
        'Walmart MASTERCARD', 'Target Credit Card', 'Presidents Choice Financial',
        'Rogers MASTERCARD', 'Premier Bankcard', 'PayPal Credit',
        'OpenSky Secured Visa Credit Card', 'Merrick Bank',
        'HomeTrust Secured VISA', 'Eppicard', 'Sears Credit Card'
    ]
    select_feature = SelectField('Choose a credit card', choices=[
                                 (x, x) for x in features])


@app.route('/')
def home():
    form = CreditCardForm(request.form)
    return render_template('home.html', form=form)


@app.route('/output', methods=['POST'])
def output():
    form = CreditCardForm(request.form)
    feature = request.form['select_feature']
    result = get_data(data, feature)
    card = result[0]
    sentence = result[1]
    # convert string dictionary to dictionary
    topic = ast.literal_eval(result[2])
    # convert string dictionary to dictionary
    overall_senti = ast.literal_eval(result[3])
    num_review = result[4]

    return render_template('index.html',
                           card=card,
                           sentence=sentence,
                           num_review=num_review,
                           topic=topic,
                           overall_senti=overall_senti,
                           form=form)


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)  # run locally http://127.0.0.1:5000/
