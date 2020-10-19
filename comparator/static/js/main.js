$(document).ready(function () {


    // search section animations
    class Hamburger {
        constructor() {
            this.hamburger = document.querySelector('.nav__hamburger')
            this.nav = document.querySelector('.nav__list-wrapper')

            this.hamburger.addEventListener('click', () => {
                this.hamburger.classList.toggle('open');
                this.nav.classList.toggle('open');
            })
        }
    }

    const hamburger = new Hamburger();

    // icons
    $('.amazon-wrapper').click(function () {
        $(this).toggleClass('amazon-color');
        $('input#amazon').attr("checked", function (index, attr) {
            return attr == "checked" ? null : "checked";
        });
    })
    $('.ebay-wrapper').click(function () {
        $(this).toggleClass('ebay-color');
        $('input#ebay').attr("checked", function (index, attr) {
            return attr == "checked" ? null : "checked";
        });
    })
    $('.allegro-wrapper').click(function () {
        $(this).toggleClass('allegro-color');
        $('input#allegro').attr("checked", function (index, attr) {
            return attr == "checked" ? null : "checked";
        });
    })

});