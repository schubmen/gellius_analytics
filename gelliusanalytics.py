import os
import json
import xml.etree.ElementTree as ET
from cltk.stops.lat import STOPS
from cltk.tokenizers.word import WordTokenizer
from cltk import NLP
from collections import Counter

def extract_chapters(xml_file):
    print('Starting to extract the book from the XML file ... ')
    root = ET.parse(xml_file).getroot()
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    book_dict = {}
    for book in root.findall('.//tei:div[@type="textpart"][@subtype="book"]', ns):
        book_title = book.find('.//tei:head', ns).text
        chapters = []
        for chapter_div in book.findall('.//tei:div[@type="textpart"][@subtype="chapter"]', ns):
            chapter_text = ""
            for p in chapter_div.findall('.//tei:p', ns):
                for elem in p.iter():
                    if elem.text:
                        chapter_text += elem.text.strip() + " "
                    if elem.tail:
                        chapter_text += elem.tail.strip() + " "
            chapters.append(chapter_text.strip())
        book_dict[book_title] = chapters
    return book_dict



def preprocess_book(book_dict):
    print('Starting to preprocess book by filtering out the stop words and tokenize the words ...')
    cltk_nlp = NLP(language="lat")
    cltk_nlp.pipeline.processes.pop(-1)
    tokenized_book_dict = {}
    for book_title, chapters in book_dict.items():
        print('Analyzing ', book_title)
        tokenized_chapters = []
        for chapter in chapters:
            cltk_doc = cltk_nlp.analyze(text=chapter)
            tokenized_chapter = []
            for token in cltk_doc.tokens_stops_filtered:
                if token not in [".", ",", ";", "?", "!", "(", ")"]:
                    tokenized_chapter.append(token)
            tokenized_chapters.append(tokenized_chapter)
        tokenized_book_dict[book_title] = tokenized_chapters
    return tokenized_book_dict

def get_top_words_all_books(preprocessed_book):
    print('Getting the top 30 words from Noctes Atticae')
    all_tokens = [token for book_title in preprocessed_book for chapter in preprocessed_book[book_title] for token in chapter]
    word_counter = Counter(all_tokens)
    top_words = word_counter.most_common(30)
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

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xml_file = os.path.join(script_dir, 'books.xml')
    book_dict = extract_chapters(xml_file)
    json_file_preprocessed_book_dict = os.path.join(script_dir, 'preprocessed_book_dict.json')
    preprocessed_book_dict=preprocess_book(book_dict)
    with open(json_file_preprocessed_book_dict, 'w', encoding='utf-8') as f:
        json.dump(preprocessed_book_dict, f, ensure_ascii=False, indent=4)
    json_file_all_books = os.path.join(script_dir, 'top_words_all_books.json')
    top_words_all_books = get_top_words_all_books(preprocessed_book_dict)
    with open(json_file_all_books, 'w', encoding='utf-8') as f:
        json.dump(top_words_all_books, f, ensure_ascii=False, indent=4)
    json_file_per_book = os.path.join(script_dir, 'top_words_per_book.json')
    top_words_per_book = get_top_words_per_book(preprocessed_book_dict)
    with open(json_file_per_book, 'w', encoding='utf-8') as f:
        json.dump(top_words_per_book, f, ensure_ascii=False, indent=4)
    print('Work is done ...')
