document.addEventListener("DOMContentLoaded", function () {

    const overlay = document.createElement("div");

    overlay.className = "page-transition";

    const rows = 5;
    const columns = 8;

    for (let i = 0; i < rows * columns; i++) {

        const tile = document.createElement("div");

        tile.className = "transition-tile";

        overlay.appendChild(tile);
    }

    document.body.appendChild(overlay);


    /*OPEN CURRENT PAGE*/

    setTimeout(function () {

        overlay.classList.add("hide");

    }, 100);


    /*PAGE LINKS */

    const links = document.querySelectorAll("a[href]");

    links.forEach(function (link) {

        link.addEventListener("click", function (event) {

            const href = link.getAttribute("href");


            /* Ignore special links */

            if (
                !href ||
                href.startsWith("#") ||
                href.startsWith("http") ||
                href.startsWith("mailto:") ||
                href.startsWith("javascript:") ||
                link.target === "_blank"
            ) {
                return;
            }


            event.preventDefault();


            /* Remove hide = start closing */

            overlay.classList.remove("hide");


            const tiles =
                overlay.querySelectorAll(".transition-tile");


            /*
                LEFT → RIGHT

                8 columns
                5 rows
            */

            tiles.forEach(function (tile, index) {

                const column = index % columns;

                const delay = column * 45;

                tile.style.transitionDelay =
                    delay + "ms";

            });


            /* Go to next page */

            setTimeout(function () {

                window.location.href = href;

            }, 850);

        });

    });

});