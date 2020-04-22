// search section animations
if ($(window).width() <= 992) {
    $('div.nav--hamburger-icon').click( function() {
        $('nav ul').slideToggle({duration: 500, queue: false})
        $('div.line-1').toggleClass('left-opaque')
        $('div.line-2').toggleClass('c-down')
        $('div.line-3').toggleClass('c-up')

    })
}

// icons
$('.amazon-wrapper').click( function() {
    $(this).toggleClass('amazon-color');
    $('input#amazon').attr("checked",  function(index, attr){
        return attr == "checked" ? null : "checked";
    });
})
$('.ebay-wrapper').click( function() {
    $(this).toggleClass('ebay-color');
    $('input#ebay').attr("checked",  function(index, attr){
        return attr == "checked" ? null : "checked";
    });
})
$('.allegro-wrapper').click( function() {
    $(this).toggleClass('allegro-color');
    $('input#allegro').attr("checked",  function(index, attr){
        return attr == "checked" ? null : "checked";
    });
})

console.log('works?')