import os
import json
import xml.etree.ElementTree as ET
from cltk.stops.lat import STOPS
from cltk.tokenizers.word import WordTokenizer
from cltk import NLP
from collections import Counter

def extract_chapters(xml_file):
    """
    Extracts the books and chapters from the specified XML file.
    Returns a dictionary where the keys are book titles and the values
    are lists of chapter texts.
    """
    print('Starting to extract the book from the XML file ... ')
    # Parse the XML file and get the root element
    root = ET.parse(xml_file).getroot()
    # Define namespace for XML element tags
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    # Initialize an empty dictionary to hold book titles and chapter texts
    book_dict = {}
    # Find all 'book' div elements in the XML file
    for book in root.findall('.//tei:div[@type="textpart"][@subtype="book"]', ns):
        # Get the book title from the 'head' element
        book_title = book.find('.//tei:head', ns).text
        # Initialize an empty list to hold chapter texts
        chapters = []
        # Find all 'chapter' div elements in the current 'book'
        for chapter_div in book.findall('.//tei:div[@type="textpart"][@subtype="chapter"]', ns):
            # Initialize an empty string to hold chapter text
            chapter_text = ""
            # Traverse the element tree to get the text content of each 'p' element
            for p in chapter_div.findall('.//tei:p', ns):
                for elem in p.iter():
                    if elem.text:
                        chapter_text += elem.text.strip() + " "
                    if elem.tail:
                        chapter_text += elem.tail.strip() + " "
            # Append the cleaned up chapter text to the list of chapters for this book
            chapters.append(chapter_text.strip())
        # Add the book title and list of chapters to the dictionary
        book_dict[book_title] = chapters
    # Return the dictionary of books and chapters
    return book_dict

def preprocess_book(book_dict):
    """
    Preprocesses the book by filtering out the stop words, punctuation,
    and tokenizing the words. Returns a dictionary where the keys are
    book titles and the values are lists of tokenized chapter texts.
    """
    print('Starting to preprocess book by filtering out the stop words and tokenizing the words ...')
    # Initialize the CLTK NLP object with the Latin language
    cltk_nlp = NLP(language="lat")
    cltk_nlp.pipeline.processes.pop(-1)
    # Initialize the CLTK NLP object with the Latin language
    tokenized_book_dict = {}
    # Loop over each book and its chapters in the book dictionary
    for book_title, chapters in book_dict.items():
        print('Analyzing ', book_title)
        # Initialize an empty list to store the tokenized chapters for this book
        tokenized_chapters = []
        # Loop over each chapter in the book
        for chapter in chapters:
            cltk_doc = cltk_nlp.analyze(text=chapter)
            tokenized_chapter = []
            for token in cltk_doc.tokens_stops_filtered:
                # Check if the token is a punctuation mark. If it is, skip it.
                if token not in [".", ",", ";", "?", "!", "(", ")"]:
                    # If the token is not a punctuation mark, append it to the tokenized chapter
                    tokenized_chapter.append(token)
            # Append the tokenized chapter to the list of tokenized chapters for this book
            tokenized_chapters.append(tokenized_chapter)
        # Add the list of tokenized chapters for this book to the tokenized book dictionary
        tokenized_book_dict[book_title] = tokenized_chapters
    # Return the tokenized book dictionary
    return tokenized_book_dict

def get_top_words_all_books(preprocessed_book):
    print('Getting the top 100 words from Noctes Atticae')
    all_tokens = [token for book_title in preprocessed_book for chapter in preprocessed_book[book_title] for token in chapter]
    word_counter = Counter(all_tokens)
    top_words = word_counter.most_common(100)
    return top_words

def get_top_words_per_book(preprocessed_book):
    print('Getting the top 30 words from each book in Noctes Atticae')
    top_words_per_book = {}
    for book_title, chapters in preprocessed_book.items():
        all_tokens = [token for chapter in chapters for token in chapter]
        word_counter = Counter(all_tokens)
        top_words = word_counter.most_common(30)
        top_words_per_book[book_title] = top_words
    return top_words_per_book

def saveAsJSONFile(script_dir, filename, file):
    json_file = os.path.join(script_dir, filename)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(file, f, ensure_ascii=False, indent=4)
    

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xml_file = os.path.join(script_dir, 'data/books.xml')

    book_dict = extract_chapters(xml_file)
    saveAsJSONFile(script_dir, 'data/book_dict.json', book_dict)
    
    preprocessed_book_dict=preprocess_book(book_dict)
    saveAsJSONFile(script_dir, 'data/preprocessed_book_dict.json', preprocessed_book_dict)

    top_words_all_books = get_top_words_all_books(preprocessed_book_dict)
    saveAsJSONFile(script_dir, 'data/top_words_all_books.json', top_words_all_books)

    top_words_per_book = get_top_words_per_book(preprocessed_book_dict)
    saveAsJSONFile(script_dir, 'data/top_words_per_book.json', top_words_per_book)

    print('Work is done ...')
