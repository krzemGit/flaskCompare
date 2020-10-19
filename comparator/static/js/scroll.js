class Scroll {
  constructor() {
    this.scrolls = document.querySelectorAll('.scroll')

    this.scrolls.forEach(scroll => {
      scroll.addEventListener('click', () => {
        const direction = scroll.dataset.direction;
        const container = scroll.parentElement
        if (direction === "left") {
          container.scrollLeft -= container.offsetWidth;
        } else {
          container.scrollLeft += container.offsetWidth;
        }
      })
    })
  }
}

const scroll = new Scroll()