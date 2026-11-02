/* =========================================================
   ArtWalk Florence - shared JavaScript (linked on EVERY page)
   ========================================================= */

/* ---------- 1. Footer year ----------
   Puts the current year in the footer automatically. */
const yearSpan = document.getElementById("year");
if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
}

/* ---------- 2. Image slider ----------
   Only runs on pages that have a slider (the "if" check),
   so this same file can be used on every page safely. */
const slider = document.querySelector(".slider");

if (slider) {
    const slides = slider.querySelectorAll(".slide");      // all the slides
    const prevBtn = slider.querySelector(".prev");          // left arrow
    const nextBtn = slider.querySelector(".next");          // right arrow
    const dotsBox = slider.querySelector(".dots");          // container for the dots
    let current = 0;                                        // index of the visible slide
    let timer;                                              // the automatic timer

    // Create one dot button for each slide
    slides.forEach(function (slide, index) {
        const dot = document.createElement("button");
        dot.className = "dot";
        dot.type = "button";
        dot.setAttribute("aria-label", "Go to slide " + (index + 1));
        dot.addEventListener("click", function () {
            showSlide(index);
            restartTimer();
        });
        dotsBox.appendChild(dot);
    });
    const dots = dotsBox.querySelectorAll(".dot");

    // Show the slide with number "index" and hide the others
    function showSlide(index) {
        // If we go past the last slide, go back to the first (and the reverse)
        if (index >= slides.length) {
            index = 0;
        }
        if (index < 0) {
            index = slides.length - 1;
        }

        slides[current].classList.remove("active");
        dots[current].classList.remove("active");

        current = index;

        slides[current].classList.add("active");
        dots[current].classList.add("active");
    }

    // Change slide automatically every 5 seconds
    function restartTimer() {
        clearInterval(timer);
        timer = setInterval(function () {
            showSlide(current + 1);
        }, 5000);
    }

    // Arrow buttons
    nextBtn.addEventListener("click", function () {
        showSlide(current + 1);
        restartTimer();
    });

    prevBtn.addEventListener("click", function () {
        showSlide(current - 1);
        restartTimer();
    });

    // Start
    showSlide(0);
    restartTimer();
}
