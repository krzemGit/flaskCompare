let templateName = document.getElementById('identifier').getAttribute('template-name')

if (templateName == 'reload') {
    document.getElementsByTagName('select')[0].onchange = function() {
        console.log('triggered')
        this.form.submit()
    } 
} else if (templateName == 'ajax') {
    document.getElementsByTagName('select')[0].onchange = function() {
        let resultId = this.value
        console.log(resultId)

        req = $.ajax({
            url : `/ajax-request?id=${resultId}`,
            type: 'GET',
        }) 

        req.done(function(data) {
            console.log(data)
        //     // let searchContainer = $('div.search-wrapper')
        //     // searchContainer.html(data)
            $('#result-display-container').html(data)
        })
    }
}
