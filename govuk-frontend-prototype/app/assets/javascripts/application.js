let userQuestion;
let loadingSpinner;
let searchBtn;
let answerSection;
let answerTextElem;
let searchAgainBtn;

window.GOVUKPrototypeKit.documentReady(() => {
  userQuestion = document.getElementById('user-question');
  loadingSpinner = document.getElementById('loading-container');
  searchBtn =  document.getElementById('submit-question-btn');
  answerSection = document.getElementById('faq-answer');
  answerTextElem = document.getElementById('answer-text');
  searchAgainBtn =  document.getElementById('search-again-btn');
})

function requestQuestion() {
  setElementVisibility(answerTextElem, false)
  setElementVisibility(searchAgainBtn, false)

  setLoading(true);
  setElementVisibility(answerSection, true)
  sendRequest(userQuestion.value).then(data => {
    console.log('Success:', data);
    setLoading(false)
    console.log(data)
    setAnswerText(data.answer);
    setElementVisibility(answerTextElem, true)
    setElementVisibility(searchAgainBtn, true)
  })
  .catch((error) => {
    console.error('Error:', error);
    setLoading(false)
    setAnswerText('An error occurred')
    setElementVisibility(answerTextElem, true)
    setElementVisibility(searchAgainBtn, true)
  });
}

function sendRequest(question) {
  var data = {
    question: question
  };

  return fetch('http://localhost:5000/questions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  .then(response => response.json())
}

function keydownHandler(event) {
  if(event.keyCode === 13) {
    requestQuestion();
  }
}

function setLoading(loading) {
  if (loading){
    loadingSpinner.classList.remove('hidden')
    searchBtn.disabled = true
  }
  else {
    loadingSpinner.classList.add('hidden')
    searchBtn.disabled = false
  }
}

function setElementVisibility(element, isVisible) {
  if (isVisible) {
    element.classList.remove('hidden')
  } else {
    element.classList.add('hidden')
  }
}

function isVisibleElement(element) {
  return element.classList.contains('hidden')
}

function setAnswerText(text) {
  answerTextElem.innerHTML = text;
}

function resetQuestionPage() {
  setElementVisibility(answerSection, false)
  setAnswerText('')
  userQuestion.value = ''
  userQuestion.focus()
  setElementVisibility(searchAgainBtn, false)
}

