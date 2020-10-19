
class Result {
  constructor(phrase, platform, title, link, image, price) {
    this.phrase = phrase;
    this.platform = platform;
    this.title = title;
    this.link = link;
    this.image = image;
    this.price = price;
  }
}

class Search {
  constructor(username, searchTitle, phrase) {
    this.username = username !== null ? username : 'guest';
    this.searchTitle = searchTitle;
  }
}

class SaveResult {
  constructor() {
    // Result save
    this.saveButtons = document.querySelectorAll('.save-btn')
    this.saveButtons.forEach((btn) => {
      btn.addEventListener('click', () => this.collectData(event))
    })

    // Search save
    this.username = null;
    this.searchTitle = null;
    this.searchId = 'new';

    this.searchInputs = document.querySelectorAll('.search-input')
    this.searchInputs.forEach(input => {
      input.addEventListener('change', () => {
        this.setSearchAttr(input)
      })
    })

    this.searchForm = document.getElementById('search-form')
    this.submitBtn = document.getElementById('search-submit')
    this.submitBtn.addEventListener('click', (e) => {
      e.preventDefault()
      if (this.searchId === 'new') {
        this.createSearch()
      } else {
        this.identifySearch()
      }
      this.sendData()
    })

    // data for API
    this.phrase = null;
    this.result = null;
    this.search = null;
    this.newSearch = false;

    // message 
    this.messageBox = document.querySelector('span.message-text')
  }
  modifyForm = (value) => {
    console.log(value);
    if (value === 'new') {
      this.searchInputs.forEach((input, index) => {
        if (index < 2) {
          input.readOnly = false
          console.log('dodaje');
        };
      })
    } else {
      this.searchInputs.forEach((input, index) => {
        if (index < 2) {
          input.readOnly = true
          console.log('odejmuje');
        };
      })
    }
  }
  setSearchAttr = (selector) => {
    switch (selector.id) {
      case 'your-name':
        this.username = selector.value;
        break
      case 'search-title':
        this.searchTitle = selector.value;
        break
      case 'search-id':
        this.searchId = selector.value;
        this.modifyForm(selector.value)
        break
    }
  }
  collectData = (event) => {
    event.preventDefault();
    this.phrase = event.target.parentNode.dataset.phrase
    const result = new Result(
      event.target.parentNode.dataset.phrase,
      event.target.parentNode.dataset.platform,
      event.target.parentNode.dataset.title,
      event.target.parentNode.dataset.link,
      event.target.parentNode.dataset.image,
      event.target.parentNode.dataset.price,
    )
    console.log('result composed')
    this.result = result
  }
  createSearch = () => {
    this.search = new Search(this.username, this.searchTitle);
    this.newSearch = true;
    console.log('search created');
  }
  identifySearch = () => {
    this.search = {
      id: this.searchId,
    }
  }
  sendData = () => {
    console.log(this.phrase);
    console.log(this.search);
    console.log(this.result);
    fetch('/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        newSearch: this.newSearch,
        search: this.search,
        result: this.result,
      })
    })
      .then(res => res.json())
      .then(data => {
        this.messageBox.textContent = '';
        this.messageBox.textContent = data.msg;
        return data
      })
      .then(data => console.log(data))
  }
}

let save = new SaveResult()
