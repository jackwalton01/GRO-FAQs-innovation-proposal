# GRO FAQs innovation proposal

## Proposal
Thanks for taking a look at my propsal for the GRO Innovation challenge :)

This POC is based on using Microsoft's Autogen to set up a Retrival Augmented Generation AI. This can be provided a document or multiple documents via the `docs/` directory in any of the following formats: 'txt', 'json', 'csv', 'tsv', 'md', 'html', 'htm', 'rtf', 'rst', 'json', 'log', 'xml', 'yaml', 'yml' and 'pdf'. This can also be expanded to include 'docx', 'doc', 'odt', 'pptx', 'ppt', 'xlsx', 'eml', 'msg', 'epub'.

These documents will then be included in the context of the AI. The language model then uses this contex to answer user's questions. You can see in the html file of GRO's FAQ page that i have included, i have added a line that i must personally approve all certificates requested, in ()[these screenshots] you can see that this update has been sucessfully included in the AI's context.

This takes place in the backend which also runs a very simple python web server. The frontend is created using the govuk prototype kit to give the front end has the 'look and feel' of a modern gov.uk application.

## Proof of Concept
While i know code isn't required i wanted to put together a proof of concept. Both to demonstrate my proposal and to learn how to work with this kind of technology myself.

I've included install and run steps below but it does require an OpenAI API key to access a gpt-4 or gpt-35-turbo model. I can provide my key for a few test questions, but of course i didn't want to push my credentials up to Github. If you would prefer not to run the code, i've included a few screenshots of it in action at the bottom.

### Installation

Create a new empty directory.

`git clone ...`

Go into the newly created `gro-innovation-challenge` directory

`source install.sh`

(you may have to give install.sh permissions to execute)

This should install and start the back-end web server. Sometimes it takes a while to install the dependencies for AutoGen.

Once done you can exit the web server (ctrl+c) and deactivate the virtual python environment with `deactivate`

*Running in future*
In future the application can just be ran by

first activate the python environment:

`source myenv/bin/activate`

run the applicaiton

`python src/autogen-rag.py`

### In Action
