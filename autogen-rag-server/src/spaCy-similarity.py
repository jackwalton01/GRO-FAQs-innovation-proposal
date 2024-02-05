import spacy
from spacy.tokens import DocBin

nlp = spacy.load('en_core_web_md', exclude=["tagger", "parser", "senter", "attribute_ruler", "lemmatizer", "ner"])

# In the spirit of innovation, the following 2 methods were written by AI :)
def store_docs(documents, answers):
    # Load existing data if it exists
    doc_bin = DocBin(attrs=["LEMMA", "ENT_IOB", "ENT_TYPE"], store_user_data=True)
    try:
        with open('faqs.bin', 'rb') as f:
            doc_bin = DocBin().from_bytes(f.read())
    except FileNotFoundError:
        pass

    # Process and append new documents
    for doc, answer in zip(documents, answers):
        doc = nlp(doc)
        doc.user_data['answer'] = answer
        doc_bin.add(doc)

    # Save the updated data
    with open('faqs.bin', 'wb') as f:
        f.write(doc_bin.to_bytes())

def compare_new_doc(new_doc):
    with open('faqs.bin', 'rb') as f:
        doc_bin = DocBin().from_bytes(f.read())

    new_doc = nlp(new_doc)
    similarities = [(doc.text, doc.similarity(new_doc), doc.user_data['answer']) for doc in doc_bin.get_docs(nlp.vocab)]
    most_similar = max(similarities, key=lambda item:item[1])
    return most_similar

sentences = [
  "What is the GRO online ordering service?", 
  "I've lost my marriage certificate how do i get a new one?",
  "How do i order a Death Certificate?",
  "How much extra does it cost to order via the phone?",
  "How much does it cost to order a Marriage Certificate?"
]

answers = [
  "test",
  "test",
  "test",
  "test",
  "test"
]

# store_docs(sentences, answers)


# Next thing i will have to do is store the embeddings of commonly asked
# questions into a file. And also a map to the original question and answer.

# Then we compare a question's similarity to the already embedded questions

# And then if we get a < 0.8 similarity score, 
# We generate an answer to give the user
# and we embed the new question and answer

# TODO to mention in th FAQ
# This would also give us the option to re-use questions with a very high similarity
# But also possible to provide a 'answers to similar questions' section
# These answers themselves would have to have a suitable degree of difference
# Which can be determined using the same similarity tools.

# This would probably be made more effective by having AI
# Focus on keywords in the sentences to use these to compare similarity
# Or any general more specialized training of the AI


# sentences_nlp = nlp.pipe(sentences)

userQ = str(input('Enter a question and we will show you the most similar question '))
# userQ_nlp = nlp(userQ)

print(compare_new_doc(userQ))

# highestSimilarity = 0
# mostSimilarSentence = ''

# for sentence in sentences_nlp:
#   score = userQ_nlp.similarity(sentence)

#   if(score > highestSimilarity):
#     highestSimilarity = score
#     mostSimilarSentence = sentence.text

# print("The most similar sentence to: " + str(userQ) +
#       " was '" + mostSimilarSentence + "' with a similarity score of " + str(highestSimilarity))