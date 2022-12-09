import streamlit as st
from sentence_transformers import SentenceTransformer, util
import json
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from os.path import exists
from IPython.display import HTML, display
import numpy as np
import math

model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-dot-v1')

def set_css():
  display(HTML('''
  
    pre {
        white-space: pre-wrap;
    }
  
  '''))
get_ipython().events.register('pre_run_cell', set_css)

def part_to_chapter(part):
    soup = BeautifulSoup(part.get_body_content(), 'html.parser')
    paragraphs = [para.get_text().strip() for para in soup.find_all('p')]
    paragraphs = [para for para in paragraphs if len(para) > 0]
    if len(paragraphs) == 0:
        return None
    title = ' '.join([heading.get_text() for heading in soup.find_all('h1')])
    return {'title': title, 'paras': paragraphs}

min_words_per_para = 150
max_words_per_para = 500

def format_paras(chapters):
    for i in range(len(chapters)):
        for j in range(len(chapters[i]['paras'])):
            split_para = chapters[i]['paras'][j].split()
            if len(split_para) > max_words_per_para:
                chapters[i]['paras'].insert(j + 1, ' '.join(split_para[max_words_per_para:]))
                chapters[i]['paras'][j] = ' '.join(split_para[:max_words_per_para])
            k = j
            while len(chapters[i]['paras'][j].split()) < min_words_per_para and k < len(chapters[i]['paras']) - 1:
                chapters[i]['paras'][j] += '\n' + chapters[i]['paras'][k + 1]
                chapters[i]['paras'][k + 1] = ''
                k += 1            

        chapters[i]['paras'] = [para.strip() for para in chapters[i]['paras'] if len(para.strip()) > 0]
        if len(chapters[i]['title']) == 0:
            chapters[i]['title'] = '(Unnamed) Chapter {no}'.format(no=i + 1)

def print_previews(chapters):
    for (i, chapter) in enumerate(chapters):
        title = chapter['title']
        wc = len(' '.join(chapter['paras']).split(' '))
        paras = len(chapter['paras'])
        initial = chapter['paras'][0][:20]
        preview = '{}: {} | wc: {} | paras: {}\n"{}..."\n'.format(i, title, wc, paras, initial)
        print(preview)
        
def get_chapters(book_path, print_chapter_previews, first_chapter, last_chapter):
    book = epub.read_epub(book_path)
    parts = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    chapters = [part_to_chapter(part) for part in parts if part_to_chapter(part) is not None]
    last_chapter = min(last_chapter, len(chapters) - 1)
    chapters = chapters[first_chapter:last_chapter + 1]
    format_paras(chapters)
    if print_chapter_previews:
        print_previews(chapters)
    return chapters

def get_embeddings(texts):
    if type(texts) == str:
        texts = [texts]
    texts = [text.replace("\n", " ") for text in texts]
    return model.encode(texts)

def search_for_answer(question, embeddings, texts):
    question_embedding = get_embeddings(question)[0]
    distances = util.pytorch_cos_sim(question_embedding, embeddings)
    closest = np.argmax(distances)
    return texts[closest]

def run_app():
    st.title("EPUB Question Answering")
    uploaded_file = st.file_uploader("Choose an EPUB file", type="epub")

    if uploaded_file is not None:
        st.write("Uploaded file:", uploaded_file.name)
        chapters = get_chapters(uploaded_file, False, 0, 0)
        texts = [' '.join(chapter['paras']) for chapter in chapters]
        embeddings = get_embeddings(texts)

        question = st.text_input("Ask a question")
        if question:
            answer = search_for_answer(question, embeddings, texts)
            st.text(answer)

if __name__ == "__main__":
    run_app()
