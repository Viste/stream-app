$(document).ready(() => {
    $('body').on('click', '#mobmenuburger', function (event) {
        event.preventDefault()
        $('body').find('.mobmenuburgermainnavbar').show()
    })
    $('body').on('click', '#mmnmnhclosemenu', function (event) {
        event.preventDefault()
        $('body').find('.mobmenuburgermainnavbar').hide()
    })
    $('body').on('click', '.mmbmn-header', function (event) {
        event.preventDefault()
        $('body').find('.mobmenuburgermainnavbar').hide()
    })

    $(document).mouseup(function (e) {
        let mobmenuburgermainnavbar = $('body').find('.mobmenuburgermainnavbar')
        if (mobmenuburgermainnavbar.has(e.target).length === 0) {
            mobmenuburgermainnavbar.hide()
            mobmenuburgermainnavbar.find('.titlePopupBlock').text('')
            mobmenuburgermainnavbar.find('.popupContent').html('')
        }
    });
    if ($(window).width() < 1025) {
        $('body').on('click', '.prod-elem .pe-previewImage', function (event) {
            event.preventDefault()
            let fadecontainer = $('body').find('#faderout')
            let title = $(this).parent().find('.buyb-left.title')
            title = title[0].innerText
            let titlecontainer = fadecontainer.find('.titlePopupBlock')
            titlecontainer.text(title)
            let content = $(this).parent().find('.annotation')

            content = content[0].innerHTML

            fadecontainer.find('.popupContent').html(content)
            fadecontainer.show()
        })

        $('body').on('click', '.closePopupButton', function (event) {
            event.preventDefault();
            let fadecontainer = $('body').find('#faderout')
            fadecontainer.hide();
            fadecontainer.find('.titlePopupBlock').text('')
            fadecontainer.find('.popupContent').html('')
        })
        $(document).mouseup(function (e) {
            let faderout = $('body').find('#faderout')
            if (faderout.has(e.target).length === 0) {
                faderout.hide()
                faderout.find('.titlePopupBlock').text('')
                faderout.find('.popupContent').html('')
            }
        });
    }
})