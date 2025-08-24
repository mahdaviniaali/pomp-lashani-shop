// Initialize Partners Slider
var partnersSwiper = new Swiper('.partners-slider', {
    slidesPerView: 2,
    spaceBetween: 20,
    loop: true,
    autoplay: {
        delay: 3000,
        disableOnInteraction: false,
    },
    pagination: {
        el: '.partners-slider .swiper-pagination',
        clickable: true,
    },
    navigation: {
        nextEl: '.partners-slider .swiper-button-next',
        prevEl: '.partners-slider .swiper-button-prev',
    },
    breakpoints: {
        576: {
            slidesPerView: 3,
        },
        768: {
            slidesPerView: 4,
        },
        992: {
            slidesPerView: 5,
        },
        1200: {
            slidesPerView: 6,
        }
    }
});

$(function () {

    $(document).ready(function () {
        // تاخیر در نمایش منو برای جلوگیری از باز و بسته شدن ناخواسته
        $('.dropdown-hover').hover(
            function () {
                $(this).find('.dropdown-menu').stop(true, true).fadeIn(200);
            },
            function () {
                $(this).find('.dropdown-menu').stop(true, true).fadeOut(200);
            }
        );

        // نمایش زیرمنوها در موبایل با کلیک
        if ($(window).width() < 992) {
            $('.dropdown-toggle').on('click', function (e) {
                e.preventDefault();
                $(this).next('.dropdown-menu').toggle();
            });
        }

    });
    // ------------ countdown -----------
    $(document).ready(function () {
        const second = 1000,
            minute = second * 60,
            hour = minute * 60,
            day = hour * 24;

        // تاریخ آینده (مثال: 1 ماه بعد از امروز)
        let countDown = new Date();
        countDown.setMonth(countDown.getMonth() + 1);
        countDown = countDown.getTime();

        let x = setInterval(function () {
            let now = new Date().getTime(),
                distance = countDown - now;

            // بررسی وجود عناصر قبل از آپدیت
            const daysEl = document.getElementById('days');
            const hoursEl = document.getElementById('hours');
            const minutesEl = document.getElementById('minutes');
            const secondsEl = document.getElementById('seconds');

            if (daysEl && hoursEl && minutesEl && secondsEl) {
                daysEl.innerText = Math.floor(distance / day);
                hoursEl.innerText = Math.floor((distance % day) / hour);
                minutesEl.innerText = Math.floor((distance % hour) / minute);
                secondsEl.innerText = Math.floor((distance % minute) / second);
            }

            if (distance < 0) {
                clearInterval(x);
                if (daysEl) daysEl.innerText = '0';
                if (hoursEl) hoursEl.innerText = '0';
                if (minutesEl) minutesEl.innerText = '0';
                if (secondsEl) secondsEl.innerText = '0';
                console.log('Countdown finished!');
            }
        }, second);
    });

});


$(document).ready(function () {
    var navMobile = document.getElementById('nav-mobile');
    if (navMobile && window.location.pathname.startsWith('/product/')) {
        navMobile.style.borderRadius = '0 !important';
    }
});


// ------------ swiper sliders -----------
$(document).ready(function () {

    // ------------ tc-header-style1 -----------
    var swiper = new Swiper('.tc-header-style1 .main-slider', {
        slidesPerView: 1,
        spaceBetween: 30,
        centeredSlides: true,
        speed: 1000,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            prevEl: '.swiper-button-next',
            nextEl: '.swiper-button-prev',
        },
        mousewheel: false,
        keyboard: true,
        autoplay: {
            delay: 5000,
        },
        loop: true,
    });

        // ------------ tc-weekly-deals-style1-----------
    var swiper = new Swiper('.tc-weekly-deals-style1 .deals-cards-mobile', {
        slidesPerView: 2,
        spaceBetween: 30,
        // centeredSlides: true,
        speed: 1000,
        pagination: false,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            prevEl: '.swiper-button-next',
            nextEl: '.swiper-button-prev',
        },
        mousewheel: false,
        keyboard: true,
        autoplay: {
            delay: 5000,
        },
        loop: true,
    });

    // ------------ tc-best-seller-style1 -----------
    var swiper = new Swiper('.tc-best-seller-style1 .products-slider', {
        slidesPerView: 5,
        spaceBetween: 30,
        // centeredSlides: true,
        speed: 1000,
        pagination: false,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            prevEl: '.swiper-button-next',
            nextEl: '.swiper-button-prev',
        },
        mousewheel: false,
        keyboard: true,
        autoplay: {
            delay: 5000,
        },
        loop: true,
        breakpoints: {
            0: {
                slidesPerView: 1,
            },
            480: {
                slidesPerView: 2,
            },
            787: {
                slidesPerView: 3,
            },
            991: {
                slidesPerView: 4,
            },
            1200: {
                slidesPerView: 5,
            }
        }
    });


    // ------------ tc-pupolar-brands-style1 -----------
    var swiper = new Swiper('.tc-pupolar-brands-style1 .pupolar-slider', {
        slidesPerView: 5,
        spaceBetween: 30,
        centeredSlides: true,
        speed: 1000,
        pagination: false,
        pagination: false,
        navigation: {
            prevEl: '.swiper-button-next',
            nextEl: '.swiper-button-prev',
        },
        mousewheel: false,
        keyboard: true,
        autoplay: {
            delay: 5000,
        },
        loop: true,
        breakpoints: {
            0: {
                slidesPerView: 1,
            },
            480: {
                slidesPerView: 2,
            },
            787: {
                slidesPerView: 4,
            },
            991: {
                slidesPerView: 5,
            },
            1200: {
                slidesPerView: 6,
            }
        }
    });


    // ------------ tc-best-single-style1 -----------
    var swiper = new Swiper('.tc-best-single-style1 .best-single-slider', {
        slidesPerView: 3,
        spaceBetween: 20,
        centeredSlides: true,
        speed: 1000,
        pagination: false,
        pagination: false,
        rtl: false,
        navigation: {
            nextEl: '.swiper-next',
            prevEl: '.swiper-prev',
        },
        mousewheel: false,
        keyboard: true,
        autoplay: {
            delay: 5000,
        },
        loop: true,
        breakpoints: {
            0: {
                slidesPerView: 1,
            },
            480: {
                slidesPerView: 2,
            },
            787: {
                slidesPerView: 3,
            },
            991: {
                slidesPerView: 3,
            },
            1200: {
                slidesPerView: 3,
            }
        }
    });


    // ------------ tc-header-style1 -----------
    var swiper = new Swiper('.tc-testimonials-style1 .blog-slider', {
        slidesPerView: 1,
        spaceBetween: 30,
        centeredSlides: true,
        speed: 1000,
        pagination: false,
        navigation: {
            prevEl: '.swiper-button-next',
            nextEl: '.swiper-button-prev',
        },
        mousewheel: false,
        keyboard: true,
        autoplay: {
            delay: 5000,
        },
        loop: true,
    });


});


document.addEventListener('DOMContentLoaded', function () {
    // تابع برای دریافت پارامترهای URL
    function getUrlParams() {
        const params = new URLSearchParams(window.location.search);
        const result = {};

        for (const [key, value] of params) {
            if (key !== 'search') { // پارامتر جستجو جداگانه مدیریت می‌شود
                result[key] = value;
            }
        }

        return result;
    }

    // افزودن پارامترهای URL به درخواست‌های HTMX
    document.body.addEventListener('htmx:configRequest', function (evt) {
        const urlParams = getUrlParams();
        Object.keys(urlParams).forEach(key => {
            if (!evt.detail.parameters[key]) {
                evt.detail.parameters[key] = urlParams[key];
            }
        });
    });

    // // مدیریت ارسال فرم
    // document.getElementById('search-form').addEventListener('submit', function (e) {
    //     e.preventDefault();
    //     // HTMX به صورت خودکار فرم را مدیریت می‌کند
    // });
});