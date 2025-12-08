function toggleMenu() {
    let dropdown = document.getElementById("dropdown");
    if (dropdown.classList.contains("show")) {
        dropdown.classList.remove("show");
    } else {
        dropdown.classList.add("show");
    }
}
