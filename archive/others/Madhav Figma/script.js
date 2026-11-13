function toggleSidebar() {
    var sidebar = document.getElementById("sidebar");
    var collapseIcon = document.getElementById("collapse-icon");
    var menuTexts = document.querySelectorAll(".menu-item-text");
    var forwardIcon = document.querySelector(".forward-icon");
    var headingText = document.querySelector(".heading-text");
    var userName = document.querySelector(".user-name");
    var crowdImage = document.getElementById("crowd-image");

    sidebar.classList.toggle("collapsed");
    collapseIcon.classList.toggle("collapsed");

    if (sidebar.classList.contains("collapsed")) {
        forwardIcon.style.display = "block";
        headingText.style.visibility = "hidden";
        menuTexts.forEach(function (item) {
            item.style.display = "none";
        });
        userName.style.visibility = "hidden"; // Hide user name when collapsed
        crowdImage.style.left = "80px"; // Adjust image position when collapsed
    } else {
        forwardIcon.style.display = "none";
        headingText.style.visibility = "visible";
        menuTexts.forEach(function (item) {
            item.style.display = "block";
        });
        userName.style.visibility = "visible"; // Show user name when expanded
        crowdImage.style.left = "297px"; // Adjust image position when expanded
    }

    // Toggle image visibility based on sidebar state
    crowdImage.style.display = sidebar.classList.contains("collapsed") ? "none" : "block";
}

function logout() {
    // Perform logout action here
    console.log("Logout clicked");
}
