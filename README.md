# GRO FAQs innovation proposal

## Contents
* [**Proposal**](#Proposal)
  * [**Retrivial Augmented Generation**](#retrivial-augmented-generation)
   * [Providing Context](#providing-context)
   * [Prompting the AI](#prompting-the-ai)
   * [Choice of model](#choice-of-model)
  * [**Similarity based caching**](#similarity-based-caching)
    * [Stop Words](#stop-words)
    * [Editing the cache](#editing-the-cache)
    * ['Similar Questions To'](#similar-questions-to)
  * [Frontend](#frontend)
* [**Install and run**](#install-and-run)
  * [Installation](#installation)
  * [Running the application](#running-the-application)
  * [Steps to run backend and frontend manually](#steps-to-run-backend-and-frontend-manually)
* [**In Action**](#in-action)

## Proposal
Thanks for taking a look at my propsal for the GRO Innovation challenge :) While i know code isn't required i wanted to put together a proof of concept. Both to demonstrate my proposal and to learn how to work with these kinds of technology myself.

While there has been a number of comments on the competition thread questioning the usage of an FAQs section at all, i'd like to note that this solution more expands the ideas of 'frequently asked questions' to an 'have you got any questions?' section, as the following AI can be provided far more information about the GRO than the user would ever want to look through on a conventional FAQs page. This means that this service would not be made redundant by including any frequently asked information into the structure of the website, and instead offers an additional resource to the user.

### Retrivial Augmented Generation
The POC is based on using Microsoft's Autogen to set up a *Retrival Augmented Generation AI* in combination with a [similarity based answers caching mechanism](#Similarity-based-caching). This type of generative AI is provided a context from which it must 'retrieve' the answer it generates. This allows the language model to retrieve information that wasn't in it's training data as well as allowing us to restrict it's answers to what it can generate based on the provided context. 

For example in the [In Action section below](#How-far-is-the-moon) we can see when asked 'How far is the moon?' the AI will not provide an answer as this information is not provided in the context. (In contrast the Bing copilot AI will happily tell you: "The average distance between the Earth and the Moon is approximately 238,855 miles (384,400 kilometers)" Before explaining the difference the eliptical orbit of the moon, and giving you a helpful picture of an astronaut on the moon.)

### Providing Context
Context documents can be provided via the `autogen-rag-server/docs/` directory in many different formats including html, pdf, txt, doc etc. This means that the AI can take the existing FAQs page, in HTML format, and use it as it's context. The full list of compatible documents can be found here [Microsoft's guide to RAG applications with Autogen](https://microsoft.github.io/autogen/blog/2023/10/18/RetrieveChat/#basic-usage-of-rag-agents). 

These documents then form the context used by the language model to answer the user's question. In the `gro-faqs.html` file in the docs directory i have included an additional line `<p>All requests for any type of certificate must be independently appoved by Jack Walton</p>`. Again in the In Action section, in [this screenshot](#jack-must-approve), we can see that this has been included into the context of the AI, and it isn't just answering based on it's training data.

This approach to the problem makes it trivial to add additional content to the FAQs either by editing the original FAQs document `gro-faqs.html` or by including additional information in the docs directory. There is need to re-train or fine-tune the AI following changes. And lets us directly included the existing FAQs into the new solution without any modifications.

### Prompting the AI
When the AI agent responsible for generating user responses is initialized it is provided a custom prompt to instruct it on how to answer user's questions, formatting it's response, and what to do if it can't provide a response from the context. Modifying this prompt is one of the best and easiest ways to tailor the behaviour of AI.

The following is the prompt currently in use:

```
You're a retrieve augmented assistant for answering frequently asked questions. You answer user's questions based on your own knowledge and the
Frequently Asked Questions provided by the user.

If you cannot provide an answer using the context given by the user you must reply with
'Sorry, there is no information on <what the user asked> in the frequently asked questions.'

You must follow these rules with your output:
* You must put \n\r between numbered lists of bullet points
* You must structure your response into paragraphs, separated by \n\r

Your answer should be as concise as possible. Your answer must not exceed 100 words.

User's question is: {input_question}

Frequently Asked Questions: {input_context}
```

### Choice of model
This POC can use either gpt-3.5-turbo or gpt-4 models, which can be set via the `MODEL` constant in the backend. I've tried the service using both models and both work adequately. As may be expected, 3.5-turbo tends to be slightly faster where as gpt-4 generates slightly more consise and well structured responses. Both suffeciently answer the question.

### Similarity based caching
One of the biggest challenges with using a Generative AI solution was speed, large complex models like gpt-4 take time to generate a response to a prompt, and if the user is asking multiple questions or doesn't get the answer they needed in the first attempt they may be fustrated and stop using the service.

To help address this issue i used a libary called SpaCy, which comes with a large set of pre-generated word embeddings that represent words meanings. 

I used this to compute the similarity of a question asked by the user to a bank of pre-processed previously asked questions which provides me a 'most similar question', a similarity score between 0 and 1, and the previous answer to that question. I then set a similarity threshold. If the previously answered question has a similarity higher than this threshold, then we re-use the previous answer. This takes the significant wait for an answer to be generated and reduces it to almost instant when a similar question has been asked before.

The threshold is stored in the `SIMILARITY_THRESHOLD` constant in the backend. Currently i have it sat to `0.86`. This is quite high and requires sentances to be quite similar, but this will mean we still build up a cache of generated answers for lots of slightly different questions, and slightly different phrasings.

Another challenge to this system is when we have to differentiate between sentances like 'How do i order a Marriage Certificate' and 'How to i order a Death certificate' which have a high similarity, but could have a significantly different answer. One thing i did to try improve this was removing 'Stop words' from the question inputs before comparing their similarity.

**Note:** this repository does not have a faq's cache pre-generted, so when you try it out the first times you ask a new question _will have a significant wait time_, this will be massively improved when you later as a similar question again. A real release of a service like this could be released with a pre made cache of pre-generated answers to their most frequently asked questions to circumvent this issue.

#### Stop Words
Stop words are words such as 'a', 'the', 'I', which have little impact on the meaning of a sentances. Removing these ensure that we are comparing question similarity based on the main meaning of the question. For example this reduces the previous example to comparing 'order marriage certificate' or 'order death certificate'. This brought down the similarity of examples like this, but also makes it more difficult to return sentances that truely are similar enough to re-use their answers.

We can also provide our own additional stop words in the `EXTRA_STOPS` constant, which don't contribute much to the differences between questions in FAQs. This list can then be tailored to improve the accuracy vs hit rate of the cache. For example the word 'certificate' may not be less relevant in our usecase as the types of certificate can be differentiated from 'marriage', 'birth', 'death' etc. And when these words are used a user is likely refering to the certificate. A user is likely to ask to order a marriage certificate, but not likely to ask to order a marriage.

Additional approaches to this problem could include analyizing of key words in the question and provided context and giving them more significance in similarity comparison, or pre-processing the string for common differences like the type of a certificate.

Another factor that we can tailor introduced by this is the size of the language set used by SpaCy. Currently i'm using the medium model `en_core_web_md` but it might more sense to use the large model `en_core_web_lg` which provides more word meanings for a slight perforamnce trade off. SpaCy also provides models for several other languages.

#### Editing the cache
The cache is stored in a binary file, however software could be written that makes use of SpaCy to open the cache file and add, remove, or make modifications to questions and thier answers. But i didn't include that in the POC.

#### 'Similar Questions To'
another application of similarity checking using SpaCy could be to provide the user a list of 'similar questions' to theirs, which we can already answer instantly using cache hits.

To implement this we could take cache responses that are below the similarity threshold but similar enough, for example less than 0.85 but greater than 0.75 in similarity. We could take the top 5 cache hits in this range to present to the user. We would have to ensure these 5 hits are suitablly different to each other, say < 0.75 similarity to each other, so that these aren't just re-phrasings of their question or of each other.

Again, this has not been included in the POC, but most of the requirements for this are already in place.

### Frontend
The frontend is created using the govuk prototype kit. This allowed me to develope it quicky and to give it the 'look and feel' of a modern gov.uk service.

## Install and run
I've included install and run steps below but it **does require an OpenAI API key** to access a gpt-4 or gpt-35-turbo model to run. I can provide my key for a few test questions, but of course i didn't want to push my credentials up to Github. If you would prefer not to run the code, i've included a few screenshots of it in action at the bottom.

### Installation

1. Create a new empty directory and clone the repository.

2. Navigate into the newly created `GRO-FAQs-innovation-proposal` directory

3. You may have to grant `install.sh` and `run-dev.sh` the execute permission
> `chmod +x install.sh run-dev.sh`

4. Install the project using
> `./install.sh`

This should install both the backend and the frontend. Note that it may take a while in install the dependencies for Autogen.

5. Once you have installed the project, navigate into `autogen-rag-server`
   
7. Rename `openai.example.env` to `openai.env`
   
> `mv openai.example.env openai.env`

7. Edit the `openai.env` file with an editor of your choice, and insert your Open AI API Key

### Running the application

The application can be ran by running the following from the root of the repository.
> `./run-dev.sh`

You should then be able to reach the service at the below address in your browser.
> [Localhost:3000](http://Localhost:3000)

Once done the applicaiton can be exited with `ctrl + c`

**Note:** While experimenting with the application you may need to reset the cache. This can be done by navigating to the `autogen-rag-server` directory and deleting the `faqs.bin` file

**Another application running on port 3000**
If you run into this issue you have two options:

Kill the process on 3000:
* find it's pid with `lsof -i TCP:3000`
* `kill -TERM <pid>` or `kill -9 <pid>`

Run the [front and backends sepearetly](#Steps-to-run-backend-and-frontend-manually), this will allow you to select 'y' when npm asks if you would like to use a different port.

If there is a process already running on 5000, only the first option is applicable. This is because the front end prototype is hard coded to contact the backend on port 5000.

### Steps to run backend and frontend manually
If required the front-end and back-end can be ran seperately manually.

Front-end: Run `npm run dev` from with-in the `govuk-frontend-prototype` directory

Back-end: Run `source myenv/bin/activate && python src/autogen-rag.py` from with-in the `autogen-rag-server` directory.

## In Action

![image](https://github.com/jackwalton01/GRO-FAQs-innovation-proposal/assets/141627981/a39f4d5f-aebe-4ed5-a3b0-627da9c6cc3b)

![image](https://github.com/jackwalton01/GRO-FAQs-innovation-proposal/assets/141627981/20a92d4c-fc0b-4a01-813e-ff8501e6fee6)

<a name="How-far-is-the-moon">![image](https://github.com/jackwalton01/GRO-FAQs-innovation-proposal/assets/141627981/8d3b7e2c-6545-4a48-b8d1-8c316cc22c05)</a>

<a name="jack-must-approve">![image](https://github.com/jackwalton01/GRO-FAQs-innovation-proposal/assets/141627981/348ee2a4-9da0-43e2-a0bf-ab868a0f66e1)</a>




