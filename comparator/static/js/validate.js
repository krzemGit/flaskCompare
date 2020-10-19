// form validation - needed here, since the form redirects to a different route
class Validate {
  constructor() {
    this.form = document.querySelector('form.home__form');
    this.errorBox = document.querySelector('div.alert');

    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      const patt = /[A-Za-z0-9]/
      if (patt.test(e.target.phrase.value) && e.target.phrase.value.length > 2) {
        e.target.submit()
      } else {
        this.errorBox.style.opacity = 1
        this.errorBox.textContent = "Phrase has to be longer than 2 characters and can only contain numbers and letters."
      }
    })
  }
}

const validate = new Validate();