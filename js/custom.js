(function ($) {

  "use strict";
    // ABOUT SLIDER
    $('body').vegas({
        slides: [
            { src: 'slide-image01.jpg' },
            { src: 'slide-image02.jpg' }
        ],
        timer: false,
        transition: [ 'zoomOut', ]
    });

})(jQuery);
