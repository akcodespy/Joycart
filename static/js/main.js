(function() {
  "use strict";


  function log() {
    if (window.console && console.log) console.log.apply(console, arguments);
  }

  document.addEventListener('DOMContentLoaded', () => {
    log('main.js loaded. path:', window.location.pathname);
    log('jQuery present?', !!window.jQuery);
    log('noUiSlider present?', !!(window.noUiSlider || (document.getElementById && document.getElementById('price-slider') && window.noUiSlider)));
    // -----------------


    const $ = window.jQuery;


    try {
      if ($) {
        $('.menu-toggle > a').on('click', function (e) {
          e.preventDefault();
          $('#responsive-nav').toggleClass('active');
        });

        // Fix cart dropdown from closing
        $('.cart-dropdown').on('click', function (e) {
          e.stopPropagation();
        });
      } else {
        log('Skipping jQuery-driven nav/cart behavior because jQuery is missing.');
      }
    } catch (err) {
      console.error('Error in jQuery nav/cart block:', err);
    }


    try {
      if ($) {
        $('.products-slick').each(function() {
          var $this = $(this),
              $nav = $this.attr('data-nav');

          $this.slick({
            slidesToShow: 4,
            slidesToScroll: 1,
            autoplay: true,
            infinite: true,
            speed: 300,
            dots: false,
            arrows: true,
            appendArrows: $nav ? $nav : false,
            responsive: [{
                breakpoint: 991,
                settings: {
                  slidesToShow: 2,
                  slidesToScroll: 1,
                }
              },
              {
                breakpoint: 480,
                settings: {
                  slidesToShow: 1,
                  slidesToScroll: 1,
                }
              },
            ]
          });
        });

        $('.products-widget-slick').each(function() {
          var $this = $(this),
              $nav = $this.attr('data-nav');

          $this.slick({
            infinite: true,
            autoplay: true,
            speed: 300,
            dots: false,
            arrows: true,
            appendArrows: $nav ? $nav : false,
          });
        });
      }
    } catch (err) {
      console.error('Error initializing slick sliders:', err);
    }


    try {
      if (document.getElementById('product-main-img')) {
        if ($) {
          $('#product-main-img').slick({
            infinite: true,
            speed: 300,
            dots: false,
            arrows: true,
            fade: true,
            asNavFor: '#product-imgs',
          });
        } else {
          log('Skipping product-main-img slick: jQuery missing.');
        }
      }

      if (document.getElementById('product-imgs')) {
        if ($) {
          $('#product-imgs').slick({
            slidesToShow: 3,
            slidesToScroll: 1,
            arrows: true,
            centerMode: true,
            focusOnSelect: true,
            centerPadding: 0,
            vertical: true,
            asNavFor: '#product-main-img',
            responsive: [{
                breakpoint: 991,
                settings: {
                  vertical: false,
                  arrows: false,
                  dots: true,
                }
              },
            ]
          });
        } else {
          log('Skipping product-imgs slick: jQuery missing.');
        }
      }

    
      var zoomMainProduct = document.getElementById('product-main-img');
      if (zoomMainProduct && $) {
        try {
          $('#product-main-img .product-preview').zoom();
        } catch (err) {
          console.warn('zoom plugin init failed:', err);
        }
      }
    } catch (err) {
      console.error('Error in product images block:', err);
    }


    try {
      if ($) {
        $('.input-number').each(function() {
          var $this = $(this),
              $input = $this.find('input[type="number"]'),
              up = $this.find('.qty-up'),
              down = $this.find('.qty-down');

          down.on('click', function () {
            var value = parseInt($input.val()) - 1;
            value = value < 1 ? 1 : value;
            $input.val(value);
            $input.change();
            updatePriceSlider($this , value);
          });

          up.on('click', function () {
            var value = parseInt($input.val()) + 1;
            value = isNaN(value) ? 1 : value;
            $input.val(value);
            $input.change();
            updatePriceSlider($this , value);
          });
        });
      }
    } catch (err) {
      console.error('Error in input-number block:', err);
    }

    var priceInputMax = document.getElementById('price-max');
    var priceInputMin = document.getElementById('price-min');

    log('priceInputMin found?', !!priceInputMin, 'priceInputMax found?', !!priceInputMax);

    if (priceInputMax) {
      priceInputMax.addEventListener('change', function(){
        try {
          updatePriceSlider($(this).parent(), this.value);
        } catch (err) {
          console.error('priceInputMax handler error:', err);
        }
      });
    }

    if (priceInputMin) {
      priceInputMin.addEventListener('change', function(){
        try {
          updatePriceSlider($(this).parent(), this.value);
        } catch (err) {
          console.error('priceInputMin handler error:', err);
        }
      });
    }

    function updatePriceSlider(elem, value) {
      
      try {
        if (!elem) return;
        // 
        if (typeof elem.hasClass !== 'function' && window.jQuery) elem = $(elem);

        if (!elem || typeof elem.hasClass !== 'function') return;

        if (elem.hasClass('price-min')) {
          if (priceSlider && priceSlider.noUiSlider) priceSlider.noUiSlider.set([value, null]);
        } else if (elem.hasClass('price-max')) {
          if (priceSlider && priceSlider.noUiSlider) priceSlider.noUiSlider.set([null, value]);
        }
      } catch (err) {
        console.error('updatePriceSlider error:', err, 'elem:', elem, 'value:', value);
      }
    }


    var priceSlider = document.getElementById('price-slider');
    if (priceSlider && window.noUiSlider) {
      try {
        noUiSlider.create(priceSlider, {
          start: [1, 999],
          connect: true,
          step: 1,
          range: {
            'min': 1,
            'max': 999
          }
        });

        priceSlider.noUiSlider.on('update', function(values, handle) {
          var value = values[handle];
          if (handle) {
            if (priceInputMax) priceInputMax.value = value;
          } else {
            if (priceInputMin) priceInputMin.value = value;
          }
        });
      } catch (err) {
        console.error('noUiSlider init error:', err);
      }
    } else {
      log('Skipping price slider init: price-slider present?', !!priceSlider, 'noUiSlider present?', !!window.noUiSlider);
    }


    //
    log('main.js finished init.');
  }); 
})(); 
