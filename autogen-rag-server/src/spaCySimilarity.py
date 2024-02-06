import spacy
from spacy.tokens import DocBin
from spacy.lang.en.stop_words import STOP_WORDS

nlp = spacy.load('en_core_web_md', exclude=["tagger", "parser", "senter", "attribute_ruler", "lemmatizer", "ner"])

# In the spirit of innovation, the following 2 methods were written by AI :)
def store_docs(documents, answers, fileName, extra_stop_words):
    # Load existing data if it exists
    doc_bin = DocBin(attrs=["LEMMA", "ENT_IOB", "ENT_TYPE"], store_user_data=True)
    try:
        with open(fileName + '.bin', 'rb') as f:
            doc_bin = doc_bin.from_bytes(f.read())
    except FileNotFoundError:
        pass

    # Process and append new documents
    for doc, answer in zip(documents, answers):
        original = doc
        doc = nlp(doc)
        doc = ' '.join([token.text for token in doc if token.text.lower() not in STOP_WORDS.union(extra_stop_words)])
        doc = nlp.make_doc(doc)
        doc.user_data['question'] = original
        doc.user_data['answer'] = answer
        doc_bin.add(doc)

    # Save the updated data
    with open(fileName + '.bin', 'wb') as f:
        f.write(doc_bin.to_bytes())

def compare_new_doc(new_doc, fileName, extra_stop_words):

    try:
        with open(fileName + '.bin', 'rb') as f:
            doc_bin = DocBin().from_bytes(f.read())
    except FileNotFoundError:
        print('Warning: No Cache File Found')
        return None

    new_doc = nlp(new_doc)
    new_doc = ' '.join([token.text for token in new_doc if token.text not in STOP_WORDS.union(extra_stop_words)])
    new_doc = nlp.make_doc(new_doc)
    similarities = [
        {
            'text': doc.text,
            'similarity': doc.similarity(new_doc),
            'question': doc.user_data['question'],
            'answer': doc.user_data['answer']
        } 
        for doc in doc_bin.get_docs(nlp.vocab)
    ]

    most_similar = max(similarities, key=lambda item: item['similarity'])

    return most_similar
