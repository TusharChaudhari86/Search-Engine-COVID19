(function ($) {

  "use strict";
    // ABOUT SLIDER
    $('body').vegas({
        slides: [
            { src: '/static/images/library.jpg' },
            { src: '/static/images/library2.jpg' }
        ],
        timer: false,
        transition: [ 'zoomOut', ]
    });
})(jQuery);
