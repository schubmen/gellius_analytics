import os
import xml.etree.ElementTree as ET

def extract_chapters(xml_file):
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

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xml_file = os.path.join(script_dir, 'books.xml')
    book_dict = extract_chapters(xml_file)