from flask import Flask, render_template, request
import pickle
import pandas as pd
import numpy as np
from fuzzywuzzy import process  # For fuzzy matching

# Load preprocessed data
popular_df = pd.read_pickle('popular.pkl')
similarity_scores = pd.read_pickle('similarity_scores.pkl')
books = pd.read_pickle('books.pkl')
pt = pd.read_pickle('pt.pkl')

app = Flask(__name__)

@app.route('/')
def index():
 
    return render_template(
        'index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=list(popular_df['Image-URL-M'].values),
        ratings=list(popular_df['num_ratings'].values),
        votes=list(popular_df['avg_ratings'].values)
    )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    # Fuzzy matching to find the closest match
    matches = process.extractOne(user_input, pt.index)
    
    if matches:
        matched_book, match_score = matches  # matched_book is the closest title
        if match_score < 70:  # If the match confidence is low
            return render_template('recommend.html', error="Book not found. Try searching again.")

        index = np.where(pt.index == matched_book)[0][0]
        distances = similarity_scores[index]
        similar_items = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:6]
        
        # Prepare recommended book data
        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title']))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author']))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M']))
            data.append(item)

        return render_template('recommend.html', data=data)
    else:
        return render_template('recommend.html', error="Book not found. Try searching again.")

if __name__ == '__main__':
    app.run(debug=True)
